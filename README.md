This is a personal project for learning that I have been working on for a couple months. I did codecademy but I needed to actually create something to truly learn.
The project tracks a hobby of mine selling stock options. Most brokerage sites don't track your P/L across options very well if at all.
I will probably add further explanations in the about page eventually but I need to work on other things for a bit.

Anyway, I am looking for feedback on the coding aspect mostly.

The project makes use of sqlalchemy, SQLITE, and FastAPI.

To get started install the necessary python libraries and initilize the database with database.py.
Launch the server from the projects root directory:
  uvicorn main:app --port {desired_port_number} --reload.

Project can be served to the network using the --host 0.0.0.0 switch.

Appreciate the feedback so I can learn more!

