// SHOW FILE NAME AFTER UPLOAD

document.getElementById("resumeFile").addEventListener("change",function(){

const file=this.files[0].name

document.getElementById("resumeText").innerHTML=
`<i class="fa-solid fa-file-pdf" style="color:red"></i> ${file}`

})

document.getElementById("jobFile").addEventListener("change",function(){

const file=this.files[0].name

document.getElementById("jobText").innerHTML=
`<i class="fa-solid fa-file-pdf" style="color:red"></i> ${file}`

})

/* ANALYZE BUTTON */

document.getElementById("analyzeBtn").addEventListener("click",async function(){

const resumeFile=document.getElementById("resumeFile").files[0]
const jobDescription=document.getElementById("jobDescription").value.trim()
const jobFile=document.getElementById("jobFile").files[0]

if(!resumeFile){
alert("Upload resume first")
return
}

if(!jobDescription && !jobFile){
alert("Provide job description")
return
}

document.getElementById("loading").classList.remove("hidden")
document.getElementById("results").classList.add("hidden")

const formData=new FormData()

formData.append("file",resumeFile)

if(jobDescription){
formData.append("job_description",jobDescription)
}

if(jobFile){
formData.append("job_file",jobFile)
}

try {

const response = await fetch("https://ai-resume-analyzer-eun4.onrender.com/upload", {
    method: "POST",
    body: formData
})

const text = await response.text()

console.log("STATUS:", response.status)
console.log("RESPONSE:", text)

const data = JSON.parse(text)

// SAFETY CHECK
if (!data.resume_score && data.resume_score !== 0) {
    alert("Backend Error:\n" + text)
    return
}

document.getElementById("loading").classList.add("hidden")
document.getElementById("results").classList.remove("hidden")

// SCORE
document.getElementById("score").innerText = data.resume_score + "%"

// MATCHED
const matched = document.getElementById("matchedSkills")
matched.innerHTML = ""

data.matched_skills.forEach(skill => {
    matched.innerHTML += `<li>✔ ${skill}</li>`
})

// MISSING
const missing = document.getElementById("missingSkills")
missing.innerHTML = ""

data.missing_skills.forEach(skill => {
    missing.innerHTML += `<li>✘ ${skill}</li>`
})

// SUGGESTIONS
const suggestions = document.getElementById("suggestions")
suggestions.innerHTML = ""

data.suggestions.forEach(s => {
    suggestions.innerHTML += `<p>${s}</p>`
})

}
catch(error){
    document.getElementById("loading").classList.add("hidden")
    alert("Error connecting backend")
}

})