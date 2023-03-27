# Request-Me

## Overview
RequestMe is a web application designed to help users manage their tasks more efficiently. This application enables users to assign tasks to others, such as teachers assigning tasks to students, employers assigning tasks to employees, customers assigning tasks to freelancers, trainers assigning exercise activities, and to-do lists for clients, and so on. The user fills out the task's priority and due date (optional) on the webpage, and the results are displayed in a summary table that includes the percent of completed tasks, percent of tasks by priority, and the tasks that the user must complete in the coming week. The application helps in better managing daily routines and ensures all important tasks are completed.

## Demo
To see a video demo of the application, click on this link: https://youtu.be/eEgL8BCJNC4

## Features
* User-friendly interface: The application is easy to use and navigate.
* Task assignment: Users can assign tasks to other users by filling out the "Request Form."
* Task summary: The application summarizes all tasks for easy viewing.
* Task reminders: The application reminds the user of the next 7-day deadline.
* Task priority: The application ensures the user can complete the tasks effectively by showing due date and priority.
* Workload management: The application keeps track of the user's workload.
* History tracking: The application provides a history of all completed and in-progress tasks.
## Logo
The RequestMe logo contains two key words - Notification (the bell icon) and Communication (Chat icon). The notification icon indicates that you have received a notification to remind you of the most important tasks that must be completed first, while the chat icon represents better communication among team members.

![RequestMe logo](/static/RequestMe_logo_crop.png)

## How it Works
### Sign Up
Users must sign up or create an account by providing the following details:

1. Username
1. Name
1. Surname
1. Email
1. Password
1. Verify Password

### Login
Users can sign in using the email address and password they provided during the sign-up process. The application validates the email address and password by querying data from the database under two conditions - whether or not the email exists, and is the password correct? The application redirects the user to the homepage after successful login.

### Homepage
The homepage is divided into four sections:

1. User information: This section displays the user's username, email, name, and surname.
1. Percentage of task completion.
1. Priority-based bar chart of assigned tasks: This section displays a bar chart by priority, with different colors to help the user see it more easily, and the user can move the mouse to those bars to see the percentage of task completion.
1. A summary of the tasks with a due date of less than seven days: This section displays a table of tasks that the user must complete by the end of the week. The user can learn more about each project by clicking on its name.

### History
This page displays the history of all tasks, both completed and in progress. To learn more about a project, the user can click on its name. The user can sort the data in the table by clicking on the column heading.

### Request Form
The user can fill out the request form to assign tasks to other users by providing the following information:

* Email address of the user to whom the task is assigned (email format)
* Project name
* Priority:
    * FYI – For your information
    * Low – This is a minor task.
    * Medium – a moderately important task
    * High – priority
