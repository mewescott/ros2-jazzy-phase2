# responsible for logging conveyor system events and data
# simple subscriber

import rclpy
from rclpy.node import Node
from conveyor_interfaces.msg import SystemAlert
from rclpy.qos import QoSProfile, ReliabilityPolicy

class LoggerNode(Node):
    """
    A ROS2 node that logs system alerts and events for the conveyor system.
    Subscribes to the /system_alert topic and logs received messages.
    """
    def __init__(self):
        # Initialize the node with a unique name
        super().__init__('logger_node')
        self.get_logger().info("Logger Node has been started.")

        # Create a subscription for the /system_alert topic with a custom QoS profile
        qos_profile = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        self.subscription = self.create_subscription(
            SystemAlert,
            '/system_alert',
            self.alert_callback,
            qos_profile
        )
        self.get_logger().info("System alert subscriber initialized.")

    def alert_callback(self, msg):
        """Callback function that logs received system alerts."""
        self.get_logger().info(f"Received system alert: Level={msg.level}, Message={msg.message}")
        
def main(args=None):
    """Main function to initialize the ROS2 node and spin it."""
    rclpy.init(args=args)
    logger_node = LoggerNode()
    try:
        rclpy.spin(logger_node)
    except KeyboardInterrupt:
        pass
    finally:
        logger_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()