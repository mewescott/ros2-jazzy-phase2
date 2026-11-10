# lifecycle managed node for safety supervision and control of the conveyor system
# subscribes to /box_state topic and monitors box count for overload conditions
# publishes safety alerts or takes corrective actions based on box count
# can deactivate the conveyor system if overload conditions persist

import rclpy
from rclpy.node import Node
from rclpy.lifecycle import LifecycleNode
from rclpy.lifecycle import State
from rclpy.lifecycle import TransitionCallbackReturn

from conveyor_interfaces.msg import BoxState, SystemAlert
from rclpy.qos import QoSProfile, ReliabilityPolicy

class SafetySupervisorNode(LifecycleNode):
    def __init__(self):
        super().__init__('safety_supervisor_node')
        self.declare_parameter('critical_threshold', 9)  # Default critical box count threshold
        self.critical_threshold = self.get_parameter('critical_threshold').value
        
        # define QoS profile for subscriptions and publications
        qos_profile = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        self.subscription = None
        self.alert_publisher = None
        self.get_logger().info("Safety Supervisor Node has been initialized.")
        
    def on_configure(self, state: State):
        self.get_logger().info("Configuring Safety Supervisor Node...")
        try:
            # Create a subscription to the /box_state topic
            qos_profile = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
            self.subscription = self.create_subscription(
                BoxState,
                '/box_state',
                self.box_state_callback,
                qos_profile
            )

            self.alert_publisher = self.create_publisher(SystemAlert, '/system_alert', 10)
            return TransitionCallbackReturn.SUCCESS
        except Exception as e:
            self.get_logger().error(f"Failed to configure Safety Supervisor Node: {e}")
            return TransitionCallbackReturn.FAILURE
        
    def on_activate(self, state: State):
        self.get_logger().info("Activating Safety Supervisor Node...")
        # Node is now active and can process messages
        return TransitionCallbackReturn.SUCCESS
    
    def on_deactivate(self, state: State):
        self.get_logger().info("Deactivating Safety Supervisor Node...")
        # Node is now inactive and should stop processing messages
        return TransitionCallbackReturn.SUCCESS
    
    def on_cleanup(self, state: State):
        self.get_logger().info("Cleaning up Safety Supervisor Node...")
        # Clean up resources and prepare for shutdown
        return TransitionCallbackReturn.SUCCESS
    
    def box_state_callback(self, msg: BoxState):
        """Callback function that checks box count and publishes alerts if necessary."""
        if msg.box_count >= self.critical_threshold:
            alert_msg = SystemAlert()
            alert_msg.level = "CRITICAL"
            alert_msg.message = f"Box count {msg.box_count} exceeds critical threshold {self.critical_threshold}."
            if self.alert_publisher is not None:
                self.alert_publisher.publish(alert_msg)
                self.get_logger().warn(alert_msg.message)
                
def main(args=None):
    """Main function to initialize the ROS2 lifecycle node and spin it."""
    rclpy.init(args=args)
    safety_supervisor_node = SafetySupervisorNode()
    rclpy.spin(safety_supervisor_node)
    safety_supervisor_node.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()