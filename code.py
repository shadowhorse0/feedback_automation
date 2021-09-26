from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb

import multiprocessing
import smtplib
import json
import time
from datetime import datetime
from datetime import timedelta

# gui
window = Tk()


f = open("data/data.json")
data = json.load(f)
f.close()


def gui():
    def submit():
        email = email_inp.get()
        feedback = feedback_inp.get()
        take_feedback(email, feedback)
    window.title("Enter Your Feedback.")
    window.geometry("400x400")
    window.configure(background="grey")
    Label(window, text="Email").place(x=75, y=100)
    Label(window, text="Feedback").place(x=75, y=150)
    email_inp = Entry(window, width=20)
    email_inp.place(x=175, y=100)
    feedback_inp = Entry(window, width=20)
    feedback_inp.place(x=175, y=150)
    btn = ttk.Button(window, text="submit", command=submit).place(x=150, y=250)
    window.mainloop()


def mail(sub, msg, mail_to):
    message = 'Subject: {}\n\n{}'.format(sub, msg)
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login("kiranaher2021@gmail.com", "Required@123")
    server.sendmail("kiranaher2021@gmail.com", mail_to, message)
    server.quit


def check_block(email):
    curr_dtime = datetime.now() - timedelta(hours=24)
    count = 0
    feedbacks = data['users'][email]['feedbacks']
    for key in feedbacks:
        pass_dtime = datetime.strptime(
            feedbacks[key]['date'], '%Y-%m-%d %H:%M:%S.%f')
        if (pass_dtime > curr_dtime):
            count += 1
    if count >= 2:
        data['users'][email]['blocked'] = 1
        data['users'][email]['block_time'] = datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S.%f')
        print("You are temporary blocked for 24 hrs\n")
    else:
        data['users'][email]['blocked'] = 0
        data['users'][email]['block_time'] = "NULL"


def get_ticket():
    curr_ticket = data['curr_ticket']
    new_ticket = curr_ticket + 1
    data['curr_ticket'] = new_ticket
    return new_ticket


def new_feedback(email, feedback):
    ticket = get_ticket()
    mb.showinfo("Success","Thank you for your feedback.\nYour Ticket id is: "+str(ticket)+"\nYou can track it using this id.")
    curr_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    if email not in data['users']:
        data['users'][email] = {"feedbacks": {ticket: {}}}
    data['users'][email]['feedbacks'][ticket] = {}
    data['users'][email]['feedbacks'][ticket]['feedback'] = feedback
    data['users'][email]['feedbacks'][ticket]['date'] = curr_date
    data['users'][email]['feedbacks'][ticket]['status'] = "running"
    data['users'][email]['feedbacks'][ticket]['assign'] = {
        "last_date": curr_date,
        "mail_count": 1
    }
    subject = 'Ticket - ' + str(ticket)
    message = 'From  - ' + email + "\n\n\nXXX feedback  "
    mail_s = multiprocessing.Process(
        target=mail, args=[subject, message, "panchambodake@gmail.com"])
    mail_s.start()


def take_feedback(email, feedback):
    feedback = int(feedback)
    if (feedback == 0):
        if email in data['users']:
            # checking user feedback counts
            # remainder(email,data)
            check_block(email, data)
            if not data['users'][email]['blocked']:
                new_feedback(email, feedback)
        else:
            new_feedback(email, feedback)

    else:
        mb.showinfo("Success""Thank you for your feedback.")

    # program end
    with open('data/data.json', 'w') as f:
        json.dump(data, f, indent=4)


def check_prob_sol():

    users = data['users']
    for key in users:
        user_feeds = users[key]['feedbacks']
        for ticket in user_feeds:
            curr_dtime = datetime.now() - timedelta(seconds=20)
            pass_dtime = datetime.strptime(
                user_feeds[ticket]["assign"]["last_date"], '%Y-%m-%d %H:%M:%S.%f')
            if(curr_dtime > pass_dtime):
                mail_count = user_feeds[ticket]["assign"]["mail_count"]
                if(mail_count < 2):
                    # send mail to engineer
                    email = key
                    curr_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                    data["users"][email]["feedbacks"][ticket]["assign"]["last_date"] = curr_date
                    data["users"][email]["feedbacks"][ticket]["assign"]["mail_count"] = mail_count+1
                    mail_count = data["users"][email]["feedbacks"][ticket]["assign"]["mail_count"]
                    subject = 'Ticket - ' + str(ticket)
                    message = 'From  - ' + email + "\n\n\nXXX feedback\n\n" + \
                        str(mail_count)+"nd time notifying engineer\n\nTicket-Generation-Date: " + \
                        user_feeds[ticket]["date"]
                    # incresing mail count
                    mail_s = multiprocessing.Process(
                        target=mail, args=[subject, message, "panchambodake@gmail.com"])
                    mail_s.start()
                elif(mail_count < 10):
                    # send mail to admin
                    email = key
                    curr_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                    data["users"][email]["feedbacks"][ticket]["assign"]["last_date"] = curr_date
                    data["users"][email]["feedbacks"][ticket]["assign"]["mail_count"] = mail_count+1
                    mail_count = data["users"][email]["feedbacks"][ticket]["assign"]["mail_count"]
                    subject = 'Ticket - ' + str(ticket)
                    message = 'From  - ' + email + "\n\n\nXXX feedback\n\n"+str(mail_count-2)+" time notifying admin\n\nTicket-Generation-Date: " + \
                        user_feeds[ticket]["date"] + \
                        "\n\nEngineer has been notified 2 times already, but problem not solved. So please look into it."
                    mail_s = multiprocessing.Process(
                        target=mail, args=[subject, message, "panchambodake@gmail.com"])
                    mail_s.start()
    time.sleep(60)
    check_prob_sol()


if __name__ == '__main__':
    check_p_solved = multiprocessing.Process(
        target=check_prob_sol)
    check_p_solved.start()
    gui()
