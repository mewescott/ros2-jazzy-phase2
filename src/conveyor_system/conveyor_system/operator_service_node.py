# responsible for reset service
# service server

import rclpy
from rclpy.node import Node
from conveyor_interfaces.srv import SetMode

class OperatorServiceNode(Node):
    """
    A ROS2 node that provides a service to reset the conveyor system.
    The service is available on the /reset_conveyor topic and uses the SetMode service type.
    """
    def __init__(self):
        # Initialize the node with a unique name
        super().__init__('operator_service_node')
        self.current_mode = "NORMAL"  # Default mode of the conveyor system
        
        self.get_logger().info("Operator Service Node has been started.")

        # Create a service server for the /set_mode topic
        self.srv = self.create_service(SetMode, '/set_mode', self.set_mode_callback)
        self.get_logger().info("Set mode service initialized.")

    def set_mode_callback(self, request, response):
        """Callback function that handles set mode requests."""
        mode = request.mode.upper()
        if mode in ['NORMAL', 'SLOW', 'STOP']:
            response.success = True
            response.message = f"Conveyor system mode set to {mode}. "
            self.get_logger().info(response.message)
        else:
            self.get_logger().warn(f"Received unknown mode: {request.mode}")
            response.success = False
            response.message = f"Unknown mode: {request.mode}. Conveyor system mode not set. Use \"normal\", \"slow\", or \"stop\" to control the conveyor system."
        
        return response
    
def main(args=None):
    """Main function to initialize the ROS2 node and spin it."""
    rclpy.init(args=args)
    operator_service_node = OperatorServiceNode()
    try:
        rclpy.spin(operator_service_node)
    except KeyboardInterrupt:
        pass
    finally:
        # Clean up and shut down the node
        operator_service_node.destroy_node()
        rclpy.shutdown()
        
if __name__ == '__main__':
    main()