fetch("/api/visits")
    .then(res => res.json())
    .then(data => {
        document.getElementById("count").textContent = data.visit_count;
    })
    .catch(err => {
        document.getElementById("count").textContent = "error";
        console.error(err);
    });