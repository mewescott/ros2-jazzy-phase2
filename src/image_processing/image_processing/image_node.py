#image processing node
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class ImageSubscriberNode(Node):
    def __init__(self):
        super().__init__('image_subscriber_node')
        self.subscription = self.create_subscription(
            Image,
            '/image',
            self.image_callback,
            10
        )
        self.subscription # prevent unused variable warning
        self.bridge = CvBridge()

    def image_callback(self, msg):
        try:
            # Convert ROS Image message to OpenCV image
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            # Process the image (for example convert to grayscale)
            gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            # Display the processed image
            cv2.imshow("Received Image", gray_image)
            # Wait for a key press and refresh the image window
            cv2.waitKey(1)
        except Exception as e:
            self.get_logger().error(f"Error converting image: {e}")

def main(args=None):
    rclpy.init(args=args)
    image_subscriber_node = ImageSubscriberNode()
    rclpy.spin(image_subscriber_node)
    image_subscriber_node.destroy_node()
    rclpy.shutdown()
    
if main == '__main__':
    main()