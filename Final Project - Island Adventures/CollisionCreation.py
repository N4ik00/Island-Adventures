import cv2
import numpy as np
import os
from datetime import datetime


class RectangleSelector:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise ValueError(f"Could not load image from {image_path}")

        # Scale the image to match game world size (1600x1200)
        self.image = cv2.resize(self.image, (1600, 1200))
        self.original_image = self.image.copy()

        print(f"Image scaled to game size: 1600x1200")

        self.drawing = False
        self.start_point = None
        self.end_point = None
        self.rectangles = []
        self.rect_counter = 0

        # Create output directory
        self.output_dir = "extracted_rectangles"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                # Create a copy of the original image to draw the current rectangle
                temp_image = self.original_image.copy()

                # Draw all saved rectangles
                for rect in self.rectangles:
                    cv2.rectangle(temp_image, rect[0], rect[1], (0, 255, 0), 2)

                # Draw current rectangle being drawn
                cv2.rectangle(temp_image, self.start_point, (x, y), (255, 0, 0), 2)
                self.image = temp_image

        elif event == cv2.EVENT_LBUTTONUP:
            if self.drawing:
                self.drawing = False
                self.end_point = (x, y)

                # Save the rectangle coordinates
                rect = (self.start_point, self.end_point)
                self.rectangles.append(rect)

                # Save coordinates to file (already at game scale!)
                self.save_coordinates(rect)

                # Update the display image
                cv2.rectangle(self.image, self.start_point, self.end_point, (0, 255, 0), 2)

    def save_coordinates(self, rect):
        start_x, start_y = rect[0]
        end_x, end_y = rect[1]

        # Ensure coordinates are in correct order
        x1, x2 = min(start_x, end_x), max(start_x, end_x)
        y1, y2 = min(start_y, end_y), max(start_y, end_y)
        width = x2 - x1
        height = y2 - y1

        if width > 0 and height > 0:  # Check if the rectangle has area
            # Save coordinates to file
            coord_file = "collision_rectangles2.txt"
            with open(coord_file, 'a') as f:
                f.write(f"Rectangle {self.rect_counter}: x={x1}, y={y1}, w={width}, h={height}\n")

            print(f"Saved rectangle {self.rect_counter + 1}:")
            print(f"  Coordinates: ({x1}, {y1}) to ({x2}, {y2})")
            print(f"  Dimensions: {width}x{height} pixels")

            self.rect_counter += 1

    def run(self):
        window_name = "Rectangle Selector - Click and drag to select rectangles"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(window_name, self.mouse_callback)

        print("Instructions:")
        print("- Click and drag to draw rectangles")
        print("- Each rectangle coordinates will be saved to collision_rectangles.txt")
        print("- Press 'r' to reset and clear all rectangles")
        print("- Press 'c' to clear the coordinates file")
        print("- Press 'q' or ESC to quit")
        print()

        while True:
            cv2.imshow(window_name, self.image)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q') or key == 27:  # 'q' or ESC
                break
            elif key == ord('r'):  # Reset display
                self.image = self.original_image.copy()
                self.rectangles = []
                print("Reset - display cleared (coordinates file not affected)")
            elif key == ord('c'):  # Clear coordinates file
                with open("collision_rectangles.txt", 'w') as f:
                    f.write("")  # Clear the file
                self.rect_counter = 0
                print("Cleared collision_rectangles.txt file")

        cv2.destroyAllWindows()
        print(f"\nSession completed. {self.rect_counter} rectangles saved to collision_rectangles.txt")


def main():
    # Use the Map.png file in the same directory
    image_path = "Map.png"

    try:
        selector = RectangleSelector(image_path)
        selector.run()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please make sure 'Map.png' exists in the same directory as this script.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
