
async function loadSubjects(){

const classId =
document.getElementById("classSelect").value;

if(!classId) return;

const res =
await fetch(`/api/subjects/${classId}`);

const subjects =
await res.json();

const subjectSelect =
document.getElementById("subjectSelect");

subjectSelect.innerHTML =
"<option value=''>Select Subject</option>";

subjects.forEach(s=>{

subjectSelect.innerHTML +=
`<option value="${s.id}">
${s.name}
</option>`;

});

document.getElementById("chapterSelect").innerHTML="";
document.getElementById("notesList").innerHTML="";

}



async function loadChapters(){

const subjectId =
document.getElementById("subjectSelect").value;

if(!subjectId) return;

const res =
await fetch(`/api/chapters/${subjectId}`);

const chapters =
await res.json();

const chapterSelect =
document.getElementById("chapterSelect");

chapterSelect.innerHTML =
"<option value=''>Select Chapter</option>";

chapters.forEach(c=>{

chapterSelect.innerHTML +=
`<option value="${c.id}">
${c.name}
</option>`;

});

document.getElementById("notesList").innerHTML="";

}


// STUDENT BUTTON

function startStudent(){

window.location.href = "/student";

}


// ADMIN POPUP OPEN

function openAdminPopup(){

document.getElementById("adminPopup").style.display = "block";

}


// ADMIN POPUP CLOSE

function closeAdminPopup(){

document.getElementById("adminPopup").style.display = "none";

}


async function loadNotes(){

const chapterId =
document.getElementById("chapterSelect").value;

if(!chapterId) return;

const res =
await fetch(`/api/notes/${chapterId}`);

const notes =
await res.json();

const container =
document.getElementById("notesList");

container.innerHTML="";

notes.forEach(n=>{

container.innerHTML += `

<div class="card">

<h4>${n.title}</h4>

<a href="/view/${n.filename}" target="_blank">
View Online
</a>

&nbsp;&nbsp;

<a href="/download/${n.filename}">
Download
</a>

</div>

`;

});

}
