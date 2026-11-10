import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort

class ObjectCountingNode(Node):
    def __init__(self):
        super().__init__('object_counting_node')
        self.subscription = self.create_subscription(
            Image,
            '/image',
            self.image_callback,
                10)
        self.publisher = self.create_publisher(
            Image,
            '/object_counting/image',
            10)
        self.bridge = CvBridge()
        self.model = YOLO('yolov8n.pt')  # Load YOLOv8 model
        self.tracker = DeepSort(max_age=30)  # Initialize DeepSORT tracker
        self.object_counts = set()  # Set to hold unique object IDs for counting
        self.count = 0  # Initialize count of unique objects
        self.line_y = 250  # Y-coordinate of the counting line

    def image_callback(self, msg):
        # Convert ROS Image message to OpenCV image
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Perform object detection
        results = self.model(cv_image)[0] # Get the first result assuming batch size of 1

        # Extract bounding boxes and class labels
        detections = []
        for box in results.boxes:
            xyxy = box.xyxy[0].tolist() # Convert the tensor containing bounding box coordinates to a list
            x1, y1, x2, y2 = xyxy # Extract coordinates from the xyxy list
            confidence = float(box.conf[0].item()) # Convert the tensor containing confidence score to a float
            class_id = int(box.cls[0].item()) # Convert the tensor containing class ID to an integer
            detections.append(([x1, y1, x2 - x1, y2 - y1], confidence, class_id)) # 

        # Update tracker with new detections
        tracks = self.tracker.update_tracks(detections, frame=cv_image) # Update the tracker with the new detections and the current frame

        # Count objects based on their class labels
        for track in tracks:
            if not track.is_confirmed():  # Skip tracks that are not confirmed
                continue
            track_id = track.track_id # Get the unique ID of the track
            l, t, w, h = track.to_ltrb()  # Get the left, top, right, and bottom coordinates of the bounding box
            center_y = (t + h) / 2  # Calculate the center y-coordinate of the bounding box
            if center_y > self.line_y and track_id not in self.object_counts: # Check if the object has crossed the line and is not already counted
                self.object_counts.add(track_id) # Add the track ID to the set of counted objects
                self.count += 1  # Increment the count of unique objects
                self.get_logger().info(f'Object ID {track_id} crossed the line. Total count: {self.count}')  # Log the event of an object crossing the line and the updated count
                
            # Draw bounding box and label on the image
            cv2.rectangle(cv_image, (int(l), int(t)), (int(l + w), int(t + h)), (0, 255, 0), 2)
            cv2.putText(cv_image, f'ID: {track_id}', (int(l), int(t) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        #     
        cv2.line(cv_image, (0, self.line_y), (cv_image.shape[1], self.line_y), (0, 0, 255), 2)  # Draw counting line
        cv2.putText(cv_image, f'Count: {self.count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2) # put count on the image

        # Publish the annotated image
        self.publisher.publish(self.bridge.cv2_to_imgmsg(cv_image, encoding='bgr8'))

        try:
            # Display the image in an OpenCV window
            cv2.namedWindow('Object Counting', cv2.WINDOW_NORMAL)
            cv2.imshow('Object Counting', cv_image)
            cv2.waitKey(1)
        except Exception as exc:
            self.get_logger().warn(f'Unable to display OpenCV window: {exc}')

        # Log the current object counts
        self.get_logger().info(f'Current object counts: {self.object_counts}')
        
def main(args=None):
    rclpy.init(args=args)
    node = ObjectCountingNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()