
function toggleDark(){

document.body.classList.toggle("dark");

localStorage.setItem(
"dark",
document.body.classList.contains("dark")
);

}

window.onload=()=>{

if(localStorage.getItem("dark")==="true"){

document.body.classList.add("dark");

}

};


/* LOAD FILES */

async function loadFiles(){

let cls=document.getElementById("classSelect").value;

let res=await fetch(`/files/${cls}`);

let files=await res.json();

let container=document.getElementById("files");

container.innerHTML="";

if(files.length===0){

container.innerHTML="<p>No files available</p>";
return;

}

files.forEach(f=>{

container.innerHTML+=`

<div class="card">

<h3>${f.topic}</h3>

<button onclick="window.open('/uploads/${f.filename}')">

View

</button>

<a href="/uploads/${f.filename}" download>

<button>

Download

</button>

</a>

</div>

`;

});

}
