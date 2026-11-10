# responsible for simulated box counting and box detection
# topic /box_state: publishes box count and overload state
# timer based publisher

import rclpy
from rclpy.node import Node
from conveyor_interfaces.msg import BoxState
from rclpy.qos import QoSProfile, ReliabilityPolicy
import random

class SensorNode(Node):
    """
    A ROS2 node that simulates box counting and detection on a conveyor belt.
    Publishes BoxState messages on the /box_state topic at regular intervals.
    """
    def __init__(self):
        # Initialize the node with a unique name
        super().__init__('sensor_node')
        self.get_logger().info("Sensor Node has been started.")

        # Allow the publish rate to be configured from the launch file.
        self.declare_parameter('publish_rate', 1.0)
        publish_rate = self.get_parameter('publish_rate').value

        # Create a publisher for the /box_state topic with a custom QoS profile
        qos_profile = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.publisher_ = self.create_publisher(BoxState, '/box_state', qos_profile)

        # Create a timer that calls publish_box_state at the configured rate
        self.timer = self.create_timer(publish_rate, self.publish_box_state)
        self.get_logger().info("Box state publisher initialized.")

    def publish_box_state(self):
        """Periodic callback that publishes a random box count."""
        # Simulate box detection by generating a random count between 0 and 10
        box_count = random.randint(0, 10)
        
        # Create a BoxState message with the box count
        msg = BoxState()
        msg.box_count = box_count
        msg.overload = box_count > 7  # Set overload flag if box count exceeds threshold
        # Publish the box state message
        self.publisher_.publish(msg)
        self.get_logger().info(f"Published box count: {box_count}")

def main(args=None):
    """Main function to initialize the ROS2 node and spin it."""
    rclpy.init(args=args)
    sensor_node = SensorNode()
    try:
        rclpy.spin(sensor_node)
    except KeyboardInterrupt:
        pass
    finally:
        # Clean up and shut down the node
        sensor_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()