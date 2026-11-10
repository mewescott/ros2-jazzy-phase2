import os
import sys

# ros2 run wrappers on Debian/Ubuntu often use /usr/bin/python3.
# If a virtualenv is active, add its site-packages before other imports so
# NumPy/SciPy and similar deps are resolved from one consistent environment.
venv = os.environ.get('VIRTUAL_ENV')
if venv:
    venv_site = os.path.join(
        venv,
        'lib',
        f'python{sys.version_info.major}.{sys.version_info.minor}',
        'site-packages',
    )
    if os.path.isdir(venv_site) and venv_site not in sys.path:
        sys.path.insert(0, venv_site)

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort

class ObjectTrackingNode(Node):
    def __init__(self):
        super().__init__('object_tracking_node')
        self.subscription = self.create_subscription(
            Image,
            '/image',
            self.image_callback,
            10)
        self.bridge = CvBridge()
        self.model = YOLO('yolov8n.pt')  # Load YOLOv8 model
        self.tracker = DeepSort(max_age=30)  # Initialize DeepSORT tracker

    def image_callback(self, msg):
        # Convert ROS Image message to OpenCV image
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Perform object detection
        results = self.model(frame)[0]  # Get the first result 

        # Extract bounding boxes, confidences, and class IDs detections= [] 
        detections = []
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()  # Get bounding box coordinates
            confidence = float(box.conf[0]) # Get confidence score
            class_id = int(box.cls[0]) # Get class ID
            # deep_sort_realtime expects: ([x, y, w, h], confidence, class_id)
            detections.append(([x1, y1, x2 - x1, y2 - y1], confidence, class_id)) 
            
        # Update tracker with detections
        tracks = self.tracker.update_tracks(detections, frame=frame)
        
        # Draw bounding boxes and track IDs on the frame
        for track in tracks:
            if not track.is_confirmed():
                continue
            track_id = track.track_id
            x1, y1, w, h = track.to_tlwh()  # Get bounding box in (x, y, w, h) format
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x1 + w), int(y1 + h)), (0, 255, 0), 2) # Draw bounding box
            cv2.putText(frame, f'ID: {track_id}', (int(x1), int(y1-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2) # Draw track ID
            
        # Display the frame with bounding boxes and track IDs
        cv2.imshow('Object Tracking', frame)
        cv2.waitKey(1)
        
def main(args=None):
    rclpy.init(args=args)
    node = ObjectTrackingNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()
    
if __name__ == '__main__':
    main()