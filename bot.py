#!/usr/bin/env python
import logging
import cv2, time
from datetime import datetime

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Configurar logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

ALLOWED_USERS_IDS = [123456789, 987654321] # Me, others
BOT_TOKEN = "YOUR TOKEN HERE" # Telegram bot token

VIDEO_DURATION = 5 # Seconds
VIDEO_DEV = 0 # Video camera /dev/video index: /dev/video0
CAMERA_RESOLUTION = (1280, 720) # Pixels

IMAGE_PATH = 'output.jpg'
VIDEO_PATH = 'output.mp4'

ROTATE = None # None (for no rotation) or cv2.ROTATE_90_COUNTERCLOCKWISE or cv2.ROTATE_90_CLOCKWISE or cv2.ROTATE_180

'''
Creates a video capture object with the correct configuration
'''
def setVideoCapture() -> cv2.VideoCapture:
    cap = cv2.VideoCapture(VIDEO_DEV)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_RESOLUTION[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_RESOLUTION[1]) 
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')) # For more speed
    cap.set(cv2.CAP_PROP_FPS, 30) # Try it, but didn't reach that

    return cap

'''
Return true if the given id is allowed to use de bot
'''
def userAllowed(user_id) -> bool:
    return user_id in ALLOWED_USERS_IDS

'''
Draws a timestamp in the given frame
'''
def burnTimestamp(frame) -> None:
    
    height, width, _ = frame.shape

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_thickness = 2
    
    text_size, _ = cv2.getTextSize(timestamp, font, font_scale, font_thickness)
    text_x = width - text_size[0] - 10
    text_y = height - 10
    
    rect_x1 = text_x - 5
    rect_y1 = text_y - text_size[1] - 5
    rect_x2 = text_x + text_size[0] + 5
    rect_y2 = text_y + 5
    
    cv2.rectangle(frame, (rect_x1, rect_y1), (rect_x2, rect_y2), (0, 125, 0), cv2.FILLED)
    cv2.putText(frame, timestamp, (text_x, text_y), font, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)

'''
Take a snapshot and stores it in IMAGE_PATH
'''
def captureImage() -> bool:
    cap = setVideoCapture()

    if not cap.isOpened():
        logger.error(f"Video device {VIDEO_DEV} not available!")
        return False

    # Get 1 sec of video and use the last frame to autoexposition done
    ts = time.time()
    while (time.time() - ts < 1):
        ret, frame = cap.read()

    # Take last frame
    if ret:
        if (ROTATE):
            frame = cv2.rotate(frame, ROTATE)

        burnTimestamp(frame)
        cv2.imwrite(IMAGE_PATH, frame)
    else:
        logger.error("Camera disconnected!")
        return False
        
    cap.release()
    return True

'''
Records a video and stores it in VIDEO_PATH
'''
def recordVideo() -> bool:

    cap = setVideoCapture()

    if not cap.isOpened():
        logger.error(f"Video device {VIDEO_DEV} not available!")
        return False

    logger.info("Starting video record...")

    frames_buffer = []
    n_frames = 0
    
    start_ts = time.time()

    while (time.time() - start_ts < VIDEO_DURATION):

        ret, frame = cap.read()
        if ret:
            frames_buffer.append(frame) 
            n_frames += 1
        else:
            logger.error("Camera disconnected!")
            return False


    fps = n_frames / VIDEO_DURATION    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    if (ROTATE == cv2.ROTATE_90_CLOCKWISE or ROTATE == cv2.ROTATE_90_COUNTERCLOCKWISE):
        out = cv2.VideoWriter(VIDEO_PATH, fourcc, fps, (CAMERA_RESOLUTION[1], CAMERA_RESOLUTION[0]))
    else:
        out = cv2.VideoWriter(VIDEO_PATH, fourcc, fps, (CAMERA_RESOLUTION[0], CAMERA_RESOLUTION[1]))
 
    # Store frames in file
    for frame in frames_buffer:

        if (ROTATE):
            frame = cv2.rotate(frame, ROTATE)

        burnTimestamp(frame)
        out.write(frame)
             
    logger.info(f"End video record. Avg fps = {fps}")

    cap.release()
    out.release()
    
    return True

'''
COMMAND /start
'''
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    logger.info("Command: /start ")

    user = update.effective_user

    if not userAllowed(user.id):
        logger.warning("User " + str(user) + "tried to use the bot without permission")
        return
  
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

'''
COMMAND /help
'''
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    logger.info("Command: /help ")

    user = update.effective_user

    if not userAllowed(user.id):
        logger.warning("User " + str(user) + "tried to use the bot without permission")
        return

    await update.message.reply_text("Available commands: \n/video\n/photo")

'''
COMMAND /video
'''
async def get_video_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    logger.info("Command: /video ")

    user = update.effective_user
    
    if not userAllowed(user.id):
        logger.warning("User " + str(user) + "tried to use the bot without permission")
        return 
    
    await update.message.reply_text(f'Recording {VIDEO_DURATION} seconds...')

    if not recordVideo():
        await update.message.reply_text('Imposible to record video now 🥲​')
        return

    await update.message.reply_text('Sending...')
    await context.bot.send_video(chat_id=update.message.chat_id, video=open(VIDEO_PATH, 'rb'), supports_streaming=True)

'''
COMMAND /photo
'''
async def get_photo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    logger.info("Command: /photo ")

    user = update.effective_user

    if not userAllowed(user.id):
        logger.warning("User " + str(user) + "tried to use the bot without permission")
        return 
    
    if not captureImage():
        await update.message.reply_text('Imposible to take photo now 🥲​')
        return

    await context.bot.send_photo(chat_id=update.message.chat_id, photo=open(IMAGE_PATH, 'rb'))


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("video", get_video_command))
    application.add_handler(CommandHandler("photo", get_photo_command))
    
    # Unknown commands / words
    application.add_handler(MessageHandler(filters.COMMAND | filters.TEXT & ~filters.COMMAND, help_command))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
