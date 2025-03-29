# socketProgramming
Group Information: Group 4

Student Name, Student ID and Email:
    Ruan Chamei 2403197 2403197@sit.singaporetech.edu.sg
    Kwek Li Xuan 2402517 2402517@sit.singaporetech.edu.sg
    Tan Yuewen, Sara 2402051 2402051@sit.singaporetech.edu.sg
    Muhammad Mikail 2403050 2403050@sit.singaporetech.edu.sg
    Joey Lim Zi Yi 2403044 2403044@sit.singaporetech.edu.sg
    Nathan Teo 2401116 2401116@sit.singaporetech.edu.sg

Instructions & Features:
    To start the server: python server.py
    To run the client: python client.py

    Logging in: L --> username --> password
        - checks for non-existing users, incorrect passwords, users already logged in
    Registering: R --> username --> password
        - checks for existing username

    Checking for Connected Users: @names

    Sending Messages: @username message
        - checks for disconnected users, non-existing users, 
    Broadcast Messages: message

    Creating Group: @group set groupname member1, member2, member3....
        - checks for existing group name, missing information
    Sending Group Message: @group send groupname message
        - checks for non-existing group name, missing information, whether user is in group
    Leaving Group: @group leave groupname
        - checks for non-existing group name, missing information, whether user is in group
        - checks for whether user is group owner --> transfer ownership to another member
    Deleting Group: @group delete groupname
        - checks for non-existing group name, missing information, whether user is group owner, whether user is in group
    Adding Member(s) to Group: @group add groupname member1, member2, member3....
        - checks for non-existing group name, missing information, whether user is group owner, whether members are already in group
    Kicking Members from Group: @group kick groupname member1, member2, member3....
        - checks for non-existing group name, missing information, whether user is group owner, whether members are in group

    Quitting (Users): @quit
    Disconnecting Users (Server): @shutdown 