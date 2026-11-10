from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Define the path to the system parameters YAML file
    config = PathJoinSubstitution(
        [FindPackageShare('conveyor_system'), 'config', 'system_params.yaml']
    )

    return LaunchDescription([
        # Launch the sensor node
        Node(
            package='conveyor_system',
            executable='sensor_node',
            name='sensor_node',
            output='screen',
            parameters=[config]
        ),
        # Launch the control node
        Node(
            package='conveyor_system',
            executable='control_node',
            name='control_node',
            output='screen',
            parameters=[config]
        ),
        # Launch the safety supervisor node
        Node(
            package='conveyor_system',
            executable='safety_supervisor_node',
            name='safety_supervisor_node',
            output='screen',
            parameters=[config]
        ),
        # Launch the operator service node
        Node(
            package='conveyor_system',
            executable='operator_service_node',
            name='operator_service_node',
            output='screen'
        ),
        # Launch the logger node
        Node(
            package='conveyor_system',
            executable='logger_node',
            name='logger_node',
            output='screen'
        ),
    ])