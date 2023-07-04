document.addEventListener('DOMContentLoaded', function() {

    const emails_view = document.querySelector('#emails-view');
    const emails_display = document.querySelector('#email-display');
    const compose_view = document.querySelector('#compose-view');

    // User button to toggle between views
    document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
    document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
    document.querySelector('#archive').addEventListener('click', () => load_mailbox('archive'));
    document.querySelector('#compose').addEventListener('click', compose_email);

    // By default, load the inbox
    load_mailbox('inbox');

    function compose_email() {
        //Show compose view and hide other views
        emails_view.style.display = 'none';
        emails_display.style.display = 'none';
        compose_view.style.display = 'block';

        // Clear out composition fields
        document.querySelector('#compose-recipients').value = '';
        document.querySelector('#compose-subject').value = '';
        document.querySelector('#compose-body').value = '';

        document.querySelector('#compose-form').onsubmit = send_email;
    }

    function send_email() {
        let recipients = document.querySelector('#compose-recipients').value;
        let subject = document.querySelector('#compose-subject').value;
        let body = document.querySelector('#compose-body').value;

        fetch('/emails', {
            method: 'POST',
            body: JSON.stringify ({
                recipients: recipients,
                subject: subject,
                body: body
            })
        })
        .then(response => response.json())
        .then(result => {
            console.log(result);
        })
        .then(() => {
            load_mailbox('sent');
        })

        return false;
    }

    function load_mailbox(mailbox) {
        // Show the mailbox and hide other views
        emails_view.style.display = 'block';
        emails_display.style.display = 'none';
        compose_view.style.display = 'none';

        // Show the mailbox name
        emails_view.innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

        fetch(`/emails/mail_list/${mailbox}`)
        .then(response => response.json())
        .then(data => {
            data.forEach(mail => {
                const di = document.createElement('div');
                di.className = 'mail';
                di.innerHTML = `<strong>${mail.subject}</strong> -from: ${mail.sender} - sent at ${mail.timestamp}`;

                // Decide background color based on read or not
                if (mail.read === false) {
                    di.style.backgroundColor = 'white';
                } else {
                    di.style.backgroundColor = 'grey';
                }

                // If user click the mail, show the content
                di.addEventListener('click', function() {
                    // Put mai.read to true
                    fetch(`/emails/mail_content/${mail.id}`, {
                        method: 'PUT',
                        body: JSON.stringify({
                            read: true
                        })
                    })
                    emails_view.style.display = 'none';
                    emails_display.style.display = 'block';
                    emails_display.innerHTML = `<div><strong>${mail.subject}</strong></div>
                        <div><i>original-sender</i>: ${mail.sender}</div>
                        <div><i>recipients</i>     : ${mail.recipients}</div>
                        <div><i>sent at</i>        : ${mail.timestamp}</div>`;
                    
                        const b = document.createElement('div');
                        b.className = 'mail_body';

                        // Add the div that contain body
                        const b_content = document.createElement('div');
                        b_content.className = 'mail_content';
                        b_content.innerHTML = `${mail.body}`;
                        b.append(b_content);

                        // Add reply button
                        const reply_btn = document.createElement('button');
                        reply_btn.className = 'reply-button';
                        reply_btn.innerHTML = 'Reply';

                        // Add eventlistener to the button
                        reply_btn.onclick = function() {
                            emails_view.style.display = 'none';
                            compose_view.style.display = 'block';
                            emails_display.style.display = 'none';

                            // Fill in composition fields
                            document.querySelector('#compose-recipients').value = mail.sender;

                            // if the subject has 'Re: ' at the position 0, keep the original subject, else add 'Re:'
                            if (mail.subject.startsWith('Re: ', 0)) {
                                document.querySelector('#compose-subject').value = `${mail.subject}`;
                            } else {
                                document.querySelector('#compose-subject').value = `Re: ${mail.subject}`;
                            }

                            // document.querySelector('#compose-subject').value = `Re: ${mail.subject}`;

                            document.querySelector('#compose-body').value = `On ${mail.timestamp} ${mail.sender} wrote: "${mail.body}"`;

                            document.querySelector('#compose-form').onsubmit = send_email;
                        }

                        b.append(reply_btn);

                        // Add archive-unarchive button
                        if (mailbox !== 'sent') {
                            if (mail.archive === false) {
                                const arc_btn = document.createElement('button');
                                arc_btn.className = 'archived-button';
                                arc_btn.innerHTML = 'Archive this mail';

                                // Add eventlistener to the button
                                arc_btn.onclick = function() {
                                    fetch(`/emails/mail_content/${mail.id}`, {
                                        method: 'PUT',
                                        body: JSON.stringify({
                                            archive: true
                                        })
                                    })
                                    .then(() => load_mailbox('inbox'))
                                }
                                b.append(arc_btn);
                            } else {
                                const un_arc = document.createElement('button');
                                un_arc.className = 'archived-button';
                                un_arc.innerHTML = 'Unarchive this mail';

                                // Add eventListener to the button
                                un_arc.addEventListener('click', function() {
                                    fetch(`/emails/mail_content/${mail.id}`, {
                                        method: 'PUT',
                                        body: JSON.stringify ({
                                            archive: false
                                        })
                                    })
                                    .then(() => load_mailbox('inbox'))
                                })

                                b.append(un_arc);
                            }
                        }

                        emails_display.append(b);

                })
                emails_view.append(di);
            });
        })
    }


    
});