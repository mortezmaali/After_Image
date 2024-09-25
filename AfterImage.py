import cv2
import numpy as np

# Video parameters
width, height = 1920, 1080  # Full HD resolution to fit most screens
fps = 30
duration_yellow = 20  # Duration of yellow screen in seconds
duration_white = 20   # Duration of white screen before text in seconds
duration_text = 10    # Duration to display the text in seconds
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 3
font_thickness = 8

# Colors
yellow = (0, 255, 255)
black = (0, 0, 0)
white = (255, 255, 255)

# Calculate the number of frames
frames_yellow = duration_yellow * fps
frames_white = duration_white * fps
frames_text = duration_text * fps

# Create video writer to save the video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter('afterimage_test.mp4', fourcc, fps, (width, height))

# Initialize window
window_name = "Afterimage Test"
cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Frame 1: Instruction to stare at the dot
yellow_screen = np.full((height, width, 3), yellow, dtype=np.uint8)
text = "Keep staring at the dot"
text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
text_x = (width - text_size[0]) // 2
text_y = (height + text_size[1]) // 2
cv2.putText(yellow_screen, text, (text_x, text_y), font, font_scale, black, font_thickness)
for _ in range(fps * 3):  # Show this frame for 3 seconds
    cv2.imshow(window_name, yellow_screen)
    video_writer.write(yellow_screen)
    if cv2.waitKey(int(1000/fps)) & 0xFF == ord('q'):
        break

# Frame 2: Yellow screen with a dot
yellow_dot_screen = np.full((height, width, 3), yellow, dtype=np.uint8)
dot_radius = 20
dot_center = (width // 2, height // 2)
cv2.circle(yellow_dot_screen, dot_center, dot_radius, black, -1)
for _ in range(frames_yellow):
    cv2.imshow(window_name, yellow_dot_screen)
    video_writer.write(yellow_dot_screen)
    if cv2.waitKey(int(1000/fps)) & 0xFF == ord('q'):
        break

# Frame 3: White screen
white_screen = np.full((height, width, 3), white, dtype=np.uint8)
for _ in range(frames_white):
    cv2.imshow(window_name, white_screen)
    video_writer.write(white_screen)
    if cv2.waitKey(int(1000/fps)) & 0xFF == ord('q'):
        break

# Frame 4: Text asking about the afterimage, split into two lines
text_afterimage_line1 = "Can you guess now what is the"
text_afterimage_line2 = "afterimage of yellow?"
text_size_line1 = cv2.getTextSize(text_afterimage_line1, font, font_scale, font_thickness)[0]
text_size_line2 = cv2.getTextSize(text_afterimage_line2, font, font_scale, font_thickness)[0]
text_x_line1 = (width - text_size_line1[0]) // 2
text_x_line2 = (width - text_size_line2[0]) // 2
text_y_line1 = (height - text_size_line1[1]) // 2
text_y_line2 = text_y_line1 + text_size_line1[1] + 50  # Adding a bit of space between the lines
cv2.putText(white_screen, text_afterimage_line1, (text_x_line1, text_y_line1), font, font_scale, black, font_thickness)
cv2.putText(white_screen, text_afterimage_line2, (text_x_line2, text_y_line2), font, font_scale, black, font_thickness)
for _ in range(frames_text):
    cv2.imshow(window_name, white_screen)
    video_writer.write(white_screen)
    if cv2.waitKey(int(1000/fps)) & 0xFF == ord('q'):
        break

# Release video writer and close the window after the video ends
video_writer.release()
cv2.destroyAllWindows()
