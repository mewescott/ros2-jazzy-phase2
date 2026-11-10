
# ROS 2 Launch file for Gazebo robot simulation
# This file launches the robot state publisher and Gazebo simulator with a robot model
# A launch file is a Python script that configures and starts multiple ROS 2 nodes and processes

# Import LaunchDescription: the main container for all launch actions
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, LogInfo, RegisterEventHandler, SetEnvironmentVariable, TimerAction
from launch.event_handlers import OnProcessExit, OnProcessStart
from launch.conditions import IfCondition
# Import Node: used to launch ROS 2 nodes (executables)
from launch_ros.actions import LifecycleNode, Node
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from lifecycle_msgs.msg import Transition
# Import ExecuteProcess: used to launch arbitrary system commands
from launch.actions import ExecuteProcess
# Import Command: allows dynamic substitution of command outputs as parameters
from launch.substitutions import Command, LaunchConfiguration
# Import ParameterValue: wraps dynamic values for ROS 2 node parameters
from launch_ros.parameter_descriptions import ParameterValue
# Import get_package_share_directory: locates the installation directory of a ROS 2 package
from ament_index_python.packages import get_package_share_directory
# Standard library imports for file operations, system processes, and temporary files
import os
import subprocess
import tempfile

def generate_robot_sdf(xacro_file):
    """Generate the SDF description of the robot from the xacro file.
    
    This function converts a URDF (Unified Robot Description Format) into SDF (Simulation Description Format)
    which is used by Gazebo for physics simulation.
    
    Args:
        xacro_file: Path to the xacro (XML macro) file containing robot definition
    """
    # Define temporary file paths for intermediate conversion steps
    robot_sdf_file = os.path.join(tempfile.gettempdir(), 'simple_robot.sdf')
    urdf_temp = os.path.join(tempfile.gettempdir(), 'simple_robot.urdf')
    
    # Execute xacro command to process the xacro file and generate URDF format
    # xacro expands macros and includes to produce a valid URDF description
    urdf = subprocess.check_output(['xacro', xacro_file], text=True)
    # Write the generated URDF to a temporary file for the next conversion step
    with open(urdf_temp, 'w', encoding='utf-8') as urdf_handle:
        urdf_handle.write(urdf)
    
    # Convert URDF to SDF format using Gazebo's command-line tool
    # The '-p' flag tells Gazebo to print the converted SDF to stdout
    sdf_output = subprocess.check_output(
        ['gz', 'sdf', '-p', urdf_temp],
        stderr=subprocess.STDOUT,
        text=True
    )
    with open(robot_sdf_file, 'w', encoding='utf-8') as sdf_handle:
        sdf_handle.write(sdf_output)
    return robot_sdf_file
        

def generate_launch_description():
    """Main launch description generator for the ROS 2 launch system.
    
    This function is called by the ROS 2 launch system and must return a LaunchDescription
    object containing all nodes and processes to be started.
    
    Returns:
        LaunchDescription: Container with all launch actions (nodes and processes)
    """
    # Get the installation directory of the robot_description package
    pkg_share = get_package_share_directory('robot_description')
    # Construct full path to the xacro file containing the robot's URDF/xacro description
    xacro_file = os.path.join(pkg_share, 'urdf', 'simple_robot.xacro')
    # Construct full path to the world file for Gazebo simulation
    world_file = os.path.join(pkg_share, 'worlds', 'simple_robot_world.sdf')
    
    try:
        # Generate the SDF description of the robot from the xacro file
        robot_sdf_file = generate_robot_sdf(xacro_file)
    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            '[robot_description] Failed to generate SDF from xacro: '
            f'Command output: \n {error.output}'
            ) from error 
    
    # Create a dynamic parameter that will execute xacro command at launch time
    # Command() allows the xacro output to be substituted as the robot_description parameter
    robot_description = ParameterValue(
        Command(['xacro ', xacro_file]),
        value_type=str)
    
    gz_verbosity = LaunchConfiguration('gz_verbosity')
    spawn_delay = LaunchConfiguration('spawn_delay')
    gz_partition = LaunchConfiguration('gz_partition')
    use_slam = LaunchConfiguration('use_slam')
    
    gz_sim = ExecuteProcess(
        cmd=['gz', 'sim', '-r', '-v', gz_verbosity, world_file],
        output='screen'
    )
    
    spawn_robot = ExecuteProcess(
        cmd=['ros2', 'run', 'ros_gz_sim', 'create',
            '-world', 'default',
            '-file', robot_sdf_file,
            '-name','simple_robot',
            '-x', '0', '-y', '0', '-z', '0.3'],
        output='screen'
    )
    
    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        output='screen',
        arguments=[
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/world/default/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo'
        ],
        remappings=[
            ('/world/default/clock', '/clock'),
        ],
    )
    
    unpause_gazebo = ExecuteProcess(
        cmd=[
            'gz', 'service',
            '-s','/world/default/control',
            '--reqtype', 'gz.msgs.WorldControl',
            '--reptype', 'gz.msgs.Boolean',
            '--timeout', '3000',
            '--req', 'pause: false',
        ],
        output='screen'
    )
    
    cmd_vel_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='cmd_vel_bridge',
        output='screen',
        # ']' means ROS -> Gazebo one-way bridge.
        # Bridge ROS /cmd_vel into Gazebo DiffDrive default model topic.
        arguments=['/model/simple_robot/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist'],
        remappings=[
            ('/model/simple_robot/cmd_vel', '/cmd_vel'),
        ],
    )
    
    slam_toolbox = LifecycleNode(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        namespace='',
        condition=IfCondition(use_slam),
        parameters=[{
            'use_sim_time': True,
            'odom_frame': 'odom',
            'base_frame': 'base_link',
            'map_frame': 'map',
            'scan_topic': '/scan',
            'mode': 'mapping',
            'resolution': 0.05,
            'max_laser_range': 10.0,
            }],
    )
    
    slam_configure = EmitEvent(
        event=ChangeState(
            lifecycle_node_matcher=lambda node: node is slam_toolbox,
            transition_id=Transition.TRANSITION_CONFIGURE,
        ),
        condition=IfCondition(use_slam),
    )
    
    slam_activate = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=slam_toolbox,
            start_state='configuring',
            goal_state='inactive',
            entities=[
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=lambda node: node is slam_toolbox,
                        transition_id=Transition.TRANSITION_ACTIVATE,
                    )
                )
            ]
        ),
        condition=IfCondition(use_slam),
    )
    
    return LaunchDescription([
        DeclareLaunchArgument(
            'gz_verbosity',
            default_value='3',
            description ='Gazebo verbosity level (0-4)'
        ),
        DeclareLaunchArgument(
            'spawn_delay',
            default_value='3.0',
            description ='Seconds to wait before spawning the robot in Gazebo'
        ),
        DeclareLaunchArgument(
            'use_slam',
            default_value='true',
            description='Whether to launch slam_toolbox and lifecycle activation events'
        ),
#        DeclareLaunchArgument(
#            'gz_partition',
#            default_value='robot_description_sim',
#            description='Gazebo transport partition to isolate this simulation instance'
#        ),
        SetEnvironmentVariable(
            'FASTDDS_BUILTIN_TRANSPORT', 'UDPv4'
        ),
        LogInfo(msg=['[robot_description] world: ', world_file]),
        LogInfo(msg=['[robot_description] xacro: ', xacro_file]),
        LogInfo(msg=['[robot_description] generated sdf: ', robot_sdf_file]),
        
        
        # Node 1: Robot State Publisher
        # Reads robot_description and publishes the robot's TF (transform) tree
        # TF tree represents the kinematic structure and transforms between robot links
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',  # Print node output to console for debugging
            parameters=[{'robot_description': robot_description,
                         'use_sim_time': True}]  # Pass the URDF/xacro as parameter
        ),

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='lidar_sensor_frame_publisher',
            output='screen',
            arguments=[
                '0', '0', '0',
                '0', '0', '0',
                'lidar_link',
                'simple_robot/base_link/lidar_sensor',
            ],
        ),
        
                
        gz_sim,
        RegisterEventHandler(
            OnProcessStart(
                target_action=gz_sim,
                on_start=[LogInfo(msg='[robot_description] Gazebo started')],
            )
        ),
        
        RegisterEventHandler(
            OnProcessExit(
                target_action=gz_sim,
                on_exit=[LogInfo(msg='[robot_description] Gazebo exited')],
            )
        ),    
        
        TimerAction(
            period=spawn_delay,
            actions=[
                LogInfo(msg='[robot_description] Spawning robot in Gazebo...'),
                spawn_robot
            ],
        ),
        
        RegisterEventHandler(
            OnProcessExit(
                target_action=spawn_robot,
                on_exit=[
                    LogInfo(
                        msg='[robot_description] Robot spawned step finished. '
                        'If /scan is empty, inspect `gz topic -i -t /scan`.'
                    ),
                    unpause_gazebo,
                ]
            )
        ),
        
        gz_bridge,
        RegisterEventHandler(
            OnProcessStart(
                target_action=gz_bridge,
                on_start=[LogInfo(msg='[robot_description] ros_gz_bridge started')]
            )
        ),
        
        cmd_vel_bridge,
        slam_toolbox,
        slam_configure,
        slam_activate
    ])