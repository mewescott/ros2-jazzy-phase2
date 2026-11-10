# python file to make robot move in a circle pattern
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist 

class CircleMover(Node):
    def __init__(self):
        super().__init__('circle_mover')
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = Twist()
        msg.linear.x = 0.5  # Move forward at 0.5 m/s
        msg.angular.z = 1.5  # Rotate at 1.5 rad/s
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg)

def main(args=None):
    rclpy.init(args=args)
    circle_mover = CircleMover()
    rclpy.spin(circle_mover)
    circle_mover.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()