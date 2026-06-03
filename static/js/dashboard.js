let emails = [];

let currentFolder = "";

let currentEmailIndex = 0;

let isSpeaking = false;

let isLoading = false;

let composeMode = false;

let composeStep = "";

let replyMode = false;

let replyEmailIndex = -1;

let searchMode = false;

let composeData = {

    to: "",

    subject: "",

    body: ""
};

window.handleCommand = handleCommand;

/* =========================
   SPEAK
========================= */

function speak(text, callback = null) {

    speechSynthesis.cancel();

    isSpeaking = true;

    const utter =
        new SpeechSynthesisUtterance(text);

    utter.lang = "en-IN";

    utter.rate = 1;

    utter.onend = () => {

        isSpeaking = false;

        if (callback)
            callback();
    };

    speechSynthesis.speak(utter);

    document.getElementById(
        "assistantText"
    ).innerText = text;
}

/* =========================
   NORMALIZE COMMAND
========================= */

function normalizeCommand(cmd) {

    cmd = cmd.toLowerCase();

    cmd = cmd

        .replace(/open sand/g, "open sent")

        

        .replace(/rash/g, "trash")

        .replace(/somebody/g, "summary")

        .replace(/summery/g, "summary")

        .replace(/reed/g, "read")

        .replace(/red/g, "read")

        .replace(/forward/g, "4")

        .replace(/sex/g, "6")

        .replace(/ate/g, "8")

        .replace(/tree/g, "3")

        .replace(/replied/g, "reply")

        .replace(/replay/g, "reply")

        .replace(/replying/g, "reply")

        .replace(/reply to/g, "reply")

        .replace(/ripley/g, "reply")

        .replace(/apply/g, "reply")

        .replace(/reply dean/g, "reply")

        .replace(/re plea/g, "reply")

        .replace(/reply t/g, "reply")

        .replace(/re ply/g, "reply")

        .replace(/to/g, "2")

        .replace(/won/g, "1")

        .replace(/\bthe\b/g, "")

        .replace(/\bplease\b/g, "")

        .replace(/\bokay\b/g, "")

        .replace(/\bok\b/g, "")

        .replace(/\s+/g, " ")

        .trim();

    return cmd;
}

/* =========================
   EXTRACT NUMBER
========================= */

function extractNumber(text) {

    text = text.toLowerCase();

    const words = {

        one: 1,
        first: 1,

        two: 2,
        second: 2,
        to: 2,
        too: 2,

        three: 3,
        third: 3,
        tree: 3,

        four: 4,
        fourth: 4,

        five: 5,
        fifth: 5,

        six: 6,
        sixth: 6,
        sex: 6,

        seven: 7,
        seventh: 7,

        eight: 8,
        eighth: 8,
        ate: 8,

        nine: 9,
        ninth: 9,

        ten: 10,
        tenth: 10,

        eleven: 11,
        eleventh: 11,

        twelve: 12,
        twelfth: 12
    };

    const match =
        text.match(/\d+/);

    if (match) {

        return parseInt(match[0]);
    }

    for (const word in words) {

        if (text.includes(word)) {

            return words[word];
        }
    }

    return null;
}

/* =========================
   FETCH FOLDER
========================= */

async function fetchFolder(folder) {

    if (isLoading)
        return;

    isLoading = true;

    currentFolder = folder;

    document.getElementById(
        "sectionTitle"
    ).innerText =
        folder.toUpperCase();

    document.getElementById(
        "sectionContent"
    ).innerHTML =
        "<p>Loading emails...</p>";

    try {

        const res = await fetch(
            `/api/gmail/${folder}`
        );

        const data = await res.json();

        if (!data.success) {

            speak(
                "Failed to fetch emails"
            );

            isLoading = false;

            return;
        }

        emails = data.emails || [];

        currentEmailIndex = 0;

        let html = "";

        emails.forEach((m, i) => {

            html += `

            <div
                class="email-item"
                onclick="readEmail(${i})"
            >

                <b>
                ${i + 1}. ${m.subject}
                </b>

                <br>

                <small>
                ${m.from}
                </small>

            </div>
            `;
        });

        document.getElementById(
            "sectionContent"
        ).innerHTML = html;

        speak(
            `${folder} opened. ${emails.length} emails loaded`
        );

    } catch (e) {

        console.log(e);

        speak(
            "Error loading emails"
        );
    }

    isLoading = false;
}

/* =========================
   READ EMAIL
========================= */

function readEmail(index) {

    if (!currentFolder) {

        speak(
            "Please open inbox or sent first"
        );

        return;
    }

    if (!emails[index]) {

        speak(
            "Email not found"
        );

        return;
    }

    currentEmailIndex = index;

    const mail = emails[index];

    const body =

        mail.body ||

        mail.snippet ||

        "No content";

    document.getElementById(
        "sectionContent"
    ).innerHTML = `

    <div class="email-item">

        <h3>${mail.subject}</h3>

        <p>

        <b>From:</b>

        ${mail.from}

        </p>

        <hr>

        <p>${body}</p>

    </div>
    `;

    speak(
        `Reading email ${index + 1}. Subject ${mail.subject}. ${body}`
    );
}

/* =========================
   SUMMARY
========================= */

async function summarizeEmail(index) {

    try {

        const res = await fetch(
            `/api/email/summary/${index}`
        );

        const data = await res.json();

        if (!data.success) {

            speak(
                "Summary failed"
            );

            return;
        }

        document.getElementById(
            "sectionContent"
        ).innerHTML = `

        <div class="email-item">

            <h3>Email Summary</h3>

            <p>${data.summary}</p>

        </div>
        `;

        speak(data.summary);

    } catch (e) {

        console.log(e);

        speak(
            "Summary failed"
        );
    }
}

/* =========================
   SUGGEST REPLY
========================= */

async function suggestReply(index) {

    try {

        const res = await fetch(
            `/api/email/reply/${index}`
        );

        const data = await res.json();

        if (!data.success) {

            speak(
                "Reply generation failed"
            );

            return;
        }

        document.getElementById(
            "sectionContent"
        ).innerHTML = `

        <div class="email-item">

            <h3>Suggested Reply</h3>

            <p>${data.reply}</p>

        </div>
        `;

        speak(data.reply);

    } catch (e) {

        console.log(e);

        speak(
            "Reply failed"
        );
    }
}





/* =========================
   SEARCH EMAILS
========================= */

function searchEmails(query) {

    query = query.toLowerCase();

    let results = emails.filter(mail => {

        let subject =
            (mail.subject || "")
            .toLowerCase();

        let sender =
            (mail.from || "")
            .toLowerCase();

        let body =
            (mail.body || "")
            .toLowerCase();

        return (

            subject.includes(query)

            ||

            sender.includes(query)

            ||

            body.includes(query)

        );

    });

    const container =
        document.getElementById(
            "sectionContent"
        );

    if (results.length === 0) {

        container.innerHTML = `

            <div class="empty-state">

                No emails found for
                "${query}"

            </div>

        `;

        speak(
            `No emails found for ${query}`
        );

        return;
    }

    speak(
        `Found ${results.length} emails for ${query}`
    );

    container.innerHTML = results.map(

        (m, i) => `

        <div class="email-item">

            <h4>
                ${i + 1}. ${m.subject}
            </h4>

            <p>
                ${m.from}
            </p>

        </div>

    `).join("");
}






/* =========================
   DELETE EMAIL
========================= */

async function deleteEmail(index){

    try{

        console.log(
            "DELETE FUNCTION CALLED"
        );

        console.log(
            "INDEX:",
            index
        );

        const response = await fetch(

            `/api/delete/${index}`,

            {
                method:"POST"
            }

        );

        const data = await response.json();

        console.log(
            "DELETE RESPONSE:",
            data
        );

        if(data.success){

            speak(
                `Email ${index + 1} moved to trash`
            );

            fetchFolder(currentFolder);

        }else{

            speak(
                "Delete failed"
            );
        }

    }catch(err){

        console.log(err);

        speak(
            "Delete failed"
        );
    }
}





/* =========================
   HANDLE COMMAND
========================= */

function handleCommand(cmd) {

    cmd = normalizeCommand(cmd);

    console.log(
        "NORMALIZED:",
        cmd
    );





        /* SEARCH EMAILS */

    if (

        cmd.startsWith("search")

    ) {

        let query = cmd.replace(
            "search",
            ""
        ).trim();

        searchEmails(query);

        return;
    }




    /* COMPOSE EMAIL */

if (

    cmd.includes("send email")

    ||

    cmd.includes("compose email")

) {

    speak(
        "Opening compose page"
    );

   window.location.href =
    "/voice-mail";

    return;
}





    /* SEND REPLY */

    if (

    cmd.startsWith("send reply")

    ) {

    console.log(
        "SEND REPLY COMMAND:",
        cmd
    );

    const parts =
        cmd.split(" ");

    const emailNumber =
        parseInt(parts[2]);

    const replyText =
        parts.slice(3).join(" ");

    console.log(
        "EMAIL NUMBER:",
        emailNumber
    );

    console.log(
        "REPLY TEXT:",
        replyText
    );

    if (

        isNaN(emailNumber)

        ||

        !emails[emailNumber - 1]

    ) {

        speak(
            "Email not found"
        );

        return;
    }

    const emailId =
        emails[emailNumber - 1].id;

    fetch(

        "/api/reply",

        {

            method: "POST",

            headers: {

                "Content-Type":
                    "application/json"

            },

            body: JSON.stringify({

                id: emailId,

                text: replyText

            })

        }

    )

    .then(response => response.json())

    .then(data => {

    console.log(
        "REPLY RESPONSE:",
        data
    );

    if (data.success) {

        speak(
            "Reply sent successfully"
        );

    } else {

        speak(
            "Reply failed"
        );

    }

})

.catch(error => {

    console.log(error);

    speak(
        "Reply sending failed"
    );

    });

     return;
    
    
    }
    
    /* OPEN INBOX */

    if (
        cmd.includes("inbox")
    ) {

        fetchFolder("inbox");

        return;
    }

    /* OPEN SENT */

    if (
        cmd.includes("sent")
    ) {

        fetchFolder("sent");

        return;
    }

    /* OPEN TRASH */

    if (
        cmd.includes("trash")
    ) {

        fetchFolder("trash");

        return;
    }

    /* DELETE EMAIL */

    if (
        cmd.startsWith("delete")
    ) {

        console.log(
            "DELETE COMMAND RECEIVED:",
            cmd
        );

        if(currentFolder === ""){

            speak(
                "Please open inbox or sent first"
            );

            return;
        }

        const n =
            extractNumber(cmd);

        console.log(
            "EXTRACTED NUMBER:",
            n
        );

        if (n == null) {

            speak(
                "Please say email number clearly"
            );

            return;
        }

        if(!emails[n - 1]){

            speak(
                `Email ${n} not found`
            );

            return;
        }

        deleteEmail(n - 1);

        return;
    }

    /* READ EMAIL */

    if (
        cmd.includes("read")
    ) {

        const n =
            extractNumber(cmd);

        if (n == null) {

            speak(
                "Please say email number clearly"
            );

            return;
        }

        readEmail(n - 1);

        return;
    }

    /* SUMMARY */

    if (
        cmd.includes("summary")
    ) {

        const n =
            extractNumber(cmd);

        if (n == null) {

            speak(
                "Please say email number clearly"
            );

            return;
        }

        summarizeEmail(n - 1);

        return;
    }

    /* SUGGEST REPLY */

    if (

    cmd.includes("suggest")

    ||

    cmd.includes("ai reply")

) {

        const n =
            extractNumber(cmd);

        if (n == null) {

            speak(
                "Please say email number clearly"
            );

            return;
        }

        suggestReply(n - 1);

        return;
    }
}

/* =========================
   INIT
========================= */

window.onload = () => {

    speak(
        "Dashboard ready. Say inbox or sent"
    );
};

/* =========================
   GLOBAL COMMAND POLLING
========================= */

let lastVoiceCommand = "";

async function pollVoiceCommands(){

    try{

        const res = await fetch(
            "/get-command"
        );

        const data = await res.json();

        const cmd = data.command;

        if(
            cmd &&
            cmd !== lastVoiceCommand
        ){

            lastVoiceCommand = cmd;

            console.log(
                "NORMALIZED:",
                cmd
            );

            document.getElementById(
                "recognizedText"
            ).innerText = cmd;

            handleCommand(cmd);

        }

    }catch(err){

        console.log(err);

    }
}

setInterval(
    pollVoiceCommands,
    500
);