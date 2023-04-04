document.addEventListener('DOMContentLoaded', () => {
    flight_duration();
});

function flight_duration() {
    document.querySelectorAll(".duration").forEach(element => {
        let time = element.dataset.value.split(":");
        element.innerText = time[0]+"h "+time[1]+"m";
    });
}


function add_passengers() {
    let div = document.querySelector('.passenger-style');
    let fname = div.querySelector('#fname');
    let lname = div.querySelector('#lname');
    let gender = div.querySelectorAll('.gender');
    let gender_val = null
    if(fname.value.trim().length === 0) {
        alert("Please enter First Name.");
        return false;
    }

    if(lname.value.trim().length === 0) {
        alert("Please enter Last Name.");
        return false;
    }

    if (!gender[0].checked) {
        if (!gender[1].checked) {
            alert("Please select gender.");
            return false;
        }
        else {
            gender_val = gender[1].value;
        }
    }
    else {
        gender_val = gender[0].value;
    }

    let passengerCount = div.parentElement.querySelectorAll(".passenger_list .each-traveller").length;

    let traveller = `<div class="row each-traveller">
                        <div>
                            <span class="traveller-name">${fname.value} ${lname.value}</span>
<!--                            <span class="traveller-gender">${gender_val}</span>-->
                        </div>
                        <input type="hidden" name="passenger${passengerCount+1}FName" value="${fname.value}">
                        <input type="hidden" name="passenger${passengerCount+1}LName" value="${lname.value}">
                        <input type="hidden" name="passenger${passengerCount+1}Gender" value="${gender_val}">
                        <div class="delete-traveller">
                            <button class="btn" type="button">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">
                                  <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5Zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5Zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6Z"/>
                                  <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1ZM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118ZM2.5 3h11V2h-11v1Z"/>
                                </svg>
                            </button>
                        </div>
                    </div>`;
    div.parentElement.querySelector(".passenger_list").innerHTML += traveller;
    div.parentElement.querySelector("#passenger_count").value = passengerCount+1;
    div.parentElement.querySelector(".traveller-head h6 span").innerText = passengerCount+1;
    div.parentElement.querySelector(".no-traveller").style.display = 'none';
    fname.value = "";
    lname.value = "";
    gender.forEach(radio => {
        radio.checked = false;
    });

    let pcount = document.querySelector("#passenger_count").value;
    let fare = document.querySelector("#basefare").value;
    let fee = document.querySelector("#fee").value;
    if (parseInt(pcount)!==0) {
        document.querySelector(".base-fare-value span").innerText = parseInt(fare)*parseInt(pcount);
        document.querySelector(".total-fare-value span").innerText = (parseInt(fare)*parseInt(pcount))+parseInt(fee);
    }

}
function proceed_payment() {
    let passenger_count = document.querySelector("#passenger_count");
    if(parseInt(passenger_count.value) > 0) {
        return true;
    }
    alert("Please add atleast one passenger.")
    return false;
}