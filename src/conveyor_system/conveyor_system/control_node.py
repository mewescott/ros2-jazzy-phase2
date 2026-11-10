# responsible for conveyor belt speed control
# topic /belt_speed: publishes the current speed of the conveyor belt
# uses multithreading
# subscribes to /box_state topic to adjust speed based on box count

import rclpy
from rclpy.node import Node
from conveyor_interfaces.msg import BoxState, BeltCommand
from rclpy.qos import QoSProfile, ReliabilityPolicy
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

class ControlNode(Node):
    """
    A ROS2 node that controls the speed of a conveyor belt based on box count.
    Publishes the current speed of the conveyor belt on the /belt_speed topic.
    Subscribes to the /box_state topic to adjust speed dynamically.
    """
    def __init__(self):
        # Initialize the node with a unique name
        super().__init__('control_node')
        self.declare_parameter('max_box_threshold', 7)  # Default maximum box count threshold
        self.declare_parameter('normal_speed', 1.0)  # Default normal speed in meters per second
        self.declare_parameter('slow_speed', 0.5)  # Default slow speed in meters per second
        
        self.max_box_threshold = self.get_parameter('max_box_threshold').get_parameter_value().integer_value
        self.normal_speed = self.get_parameter('normal_speed').get_parameter_value().double_value
        self.slow_speed = self.get_parameter('slow_speed').get_parameter_value().double_value
        
        self.get_logger().info("Control Node has been started.")

        # Create a callback group for handling callbacks in a reentrant manner
        self.callback_group = ReentrantCallbackGroup()

        # Create a publisher for the /belt_speed topic with a custom QoS profile
        qos_profile = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.publisher_ = self.create_publisher(BeltCommand, '/belt_speed', qos_profile)
        self.get_logger().info("Belt speed publisher initialized.")

        # Create a subscriber for the /box_state topic with the same QoS profile
        self.subscription = self.create_subscription(
            BoxState,
            '/box_state',
            self.box_count_callback,
            qos_profile,
            callback_group=self.callback_group
        )

        # Initialize belt speed and box count
        self.belt_speed = 1.0  # Default speed in meters per second
        self.box_count = 0

        self.get_logger().info("Belt speed controller initialized.")

    def box_count_callback(self, msg):
        """Callback function that updates box count and adjusts belt speed."""
        box_count = msg.box_count
        overload = msg.overload
        
        max_box_threshold = self.get_parameter('max_box_threshold').get_parameter_value().integer_value
        normal_speed = self.get_parameter('normal_speed').get_parameter_value().double_value
        slow_speed = self.get_parameter('slow_speed').get_parameter_value().double_value
        # Adjust belt speed based on box count (simple logic for demonstration)
        if overload:
            self.belt_speed = slow_speed  # Slow down if too many boxes
            self.get_logger().info(f'Box count {box_count} exceeds threshold. Slowing down belt to {self.belt_speed} m/s.')
        else:
            self.belt_speed = normal_speed  # Normal speed
            self.get_logger().info(f'Box count {box_count} is within threshold. Setting belt speed to {self.belt_speed} m/s.')
        speed_msg = BeltCommand()
        speed_msg.speed = self.belt_speed
        self.publisher_.publish(speed_msg)
        self.get_logger().info(f"Box count: {box_count}, Overload: {overload}, Belt speed set to: {self.belt_speed} m/s")
 
def main(args=None):
    """Main function to initialize the ROS2 node and spin it with a multi-threaded executor."""
    rclpy.init(args=args)
    control_node = ControlNode()
    executor = MultiThreadedExecutor()
    executor.add_node(control_node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        # Clean up and shut down the node
        control_node.destroy_node()
        rclpy.shutdown()    
        
if __name__ == '__main__':
    main()