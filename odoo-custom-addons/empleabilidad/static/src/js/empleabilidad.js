const NAME_REQUIRED = "Ingresar el nombre del cargo";
const EMAIL_REQUIRED = "Ingrese un email";
const EMAIL_INVALID = "Ingrese un email correcto";

const DESCRIPTION_REQUIRED = "Por favor ingrese una descripción del cargo..";
const MIS_CATEG_IDS_REQUIRED = "Se requiere al menos un cargo";

const DATE_INVALID = "Fecha invalida";
const DATE_REQUIRED = "Fecha requerida";

const CITY_REQUIRED = "Ingresar ciudad del cargo";
const SALARY_REQUIRED = "Salario invalido";

// ****


Date.prototype.toDateInputValue = function() {
    var datestring = this.getFullYear() + "-" + ("0" + (this.getMonth())).slice(-2) + "-" + ("0" + this.getDate()).slice(-2);
    return datestring;
};
Date.prototype.toDateInputValueMonth = function() {
    var datestring = this.getFullYear() + "-" + ("0" + (this.getMonth() + 1)).slice(-2) + "-" + ("0" + this.getDate()).slice(-2);
    return datestring;
};

// _LVFillSkillType();

// document.getElementById("EmpresaCandidateOportunidad").addEventListener('load', (event) =&gt; {
//    console.log('The page is fully loaded.');
//  });




window.addEventListener("load", e => {
    console.log("Evento");
    let theform = document.getElementById("EmpresaCandidateOportunidad");
    let descriptioncount = document.getElementById("description");
    let countdescription = document.getElementById("countdescription");

    let addskilltype = document.getElementById("addskilltype");
    let addskill = document.getElementById("addskill");
    let addskilllevel = document.getElementById("addskilllevel");
    let btnaddskill = document.getElementById("btnaddskill");



    //clearChildren("skilltypeDL");
    console.log("windows load _LVFillSkillType");
    _LVFillSkillType();
    //_SkillLV();
    const SkillJson = [];
    const CatJson = [];

    // TODO: prevent the form from being auto-submitted when the user  
    // clicks the Submit button or types Enter in a field
    theform.addEventListener("submit", e => {
        //e.preventDefault();
        console.log("submit button");
        //alert("Se va a avalidar submmit")

        const result = 1; // validaCantidateForm()

        //result = 1;
        console.log(" validaCantidateForm ", result);




        if (!result) {
            // stop form submission
            e.preventDefault();
        } else {
            // prepare information about array
            console.log("result else....!!")
                // alert("Psa por el result");
            const CatJson = JSON.stringify(_CategToJson(document.querySelector('#mis_categ_ids_table tbody')));
            //const CatJson = _CategToJson(document.querySelector('#mis_categ_ids_table tbody'));
            console.log("CatJson ", CatJson);
            //alert("antes la validacion skill")
            //if (document.querySelector('#skills_table tbody').children.length > 0) {
            const SkillJson = JSON.stringify(_CategToJson(document.querySelector('#skills_table tbody')));
            //} else {
            //    console.log("No se valida skillss");
            //    const SkillJson = '';
            //}
            //alert("Paso la validacion skill");
            console.log("CatJson ", CatJson);
            console.log("SkillJson ", SkillJson);
            //console.log("x_categ_dicts ", document.getElementsByName("x_categ_dicts")[0].value);
            /*
                document.getElementsByTagName("x_categ_dicts").value = CatJson;
                document.getElementsByTagName("skills").value = SkillJson;
                */
            //e.preventDefault();
            document.getElementsByName("x_categ_dicts")[0].value = CatJson;
            document.getElementsByName("x_skill_ids")[0].value = SkillJson;
            console.log("x_categ_dicts ", document.getElementsByName("x_categ_dicts")[0].value);

            //alert("This alert will never be shown.");

        }

    })

    // TODO: The change event is called when the user commits
    // a change to an input control
    // namecount.addEventListener("change",e=&gt; {
    //  let count = namecount.value.length;
    //  countfield.value = count;
    //   console.log(`Cambio el dato en el evento:${e.scrElement}`);
    //})

    descriptioncount.addEventListener("input", e => {
        let count = descriptioncount.value.length;
        if (count >= 600) {
            if (count > 700) {
                descriptioncount.classList.add("limit");
                descriptioncount.classList.remove("warning");

            } else {
                descriptioncount.classList.add("warning");
                descriptioncount.classList.remove("limit");
            }
        } else {
            descriptioncount.classList.remove("limit");
            descriptioncount.classList.remove("warning");
        }
        countdescription.value = count;
    })

    addskilltype.addEventListener("input", e => {
        console.log(" Evento input on addskilltype ");
        _LVFillSkill();
        _LVFillSkillLevel();
    });


    btnaddskill.addEventListener('click', e => {
        console.log(" Evento click on btnaddskill ");
        _AddSkill();

        btnaddskill.setAttribute('disabled', 'true');
        document.getElementById("addskill").value = [];
        document.getElementById("addskilllevel").value = [];
        document.getElementById("addskilltype").value = [];

    });


    addskilltype.addEventListener('click', e => {
        e.target.value = '';
        console.log(" Evento click on addskilltype ");
        document.getElementById("addskill").value = '';
        document.getElementById("addskilllevel").value = '';
        _LVFillSkillType();
        btnaddskill.setAttribute('disabled', 'true');
    });

    addskilltype.addEventListener('click', e => {
        e.target.select();
        console.log(" Evento click2 on addskilltype ");
        document.getElementById("addskill").value = '';
        document.getElementById("addskilllevel").value = '';
        //_SkillLV();
        _LVFillSkillLevel();
        btnaddskill.setAttribute('disabled', 'true');
    });

    addskill.addEventListener('click', e => {
        e.target.value = ''
        console.log(" Evento click on addskill ");
        document.getElementById("addskilllevel").value = '';
        _LVFillSkillLevel();
        btnaddskill.setAttribute('disabled', 'true');

    });

    addskill.addEventListener('click', e => {
        e.target.select()
        console.log(" Evento click2 on addskill ");
        document.getElementById("addskilllevel").value = '';
        _LVFillSkillLevel();
    });


    addskilllevel.addEventListener('click', e => {
        e.target.value = ''
        console.log(" Evento click on addskilllevel ");
        _LVFillSkillLevel();
        btnaddskill.setAttribute('disabled', 'true');
    });

    addskilllevel.addEventListener('click', e => {
        e.target.select()
        console.log(" Evento click2 on addskilllevel ");
        //_LVFillSkillLevel(); 
        btnaddskill.removeAttribute('disabled');

    });


    // TODO: The input event is called immediately whenever the content is modified


    // TODO: event bubbling can be used to catch events on multiple fields
    // You can also pass an object as the event listener, as long as it has
    // a handleEvent() function to receive the event callback


    if (document.getElementById("date_open").value === '') {
        console.log("Cambio de fecha date_open")
        console.log("date_open ", document.getElementById("date_open").value)
            //document.getElementById("date_open").value = new Date().toDateInputValue();
    }

    if (document.getElementById("date_closed").value === '') {
        console.log("Cambio de fecha")
        document.getElementById("date_closed").value = new Date().toDateInputValueMonth();
    }


});

class FormEventListener {
    constructor(formElem) {
        this.formElem = formElem;
    }

    // TODO: define the handleEvent function to make this object an event handler
}






// ****

// show a message with a type of the input
function showMessage(input, message, type) {
    // get the small element and set the message
    const msg = input.parentNode.querySelector("small");
    msg.innerText = message;
    // update the class for the input
    input.className = type ? "success" : "error";
    return type;
}

function showError(input, message) {
    console.log("Entro showError ")
    return showMessage(input, message, false);
}

function showSuccess(input) {
    return showMessage(input, "", true);
}

function hasValue(input, message) {
    if (input.value.trim() === "") {
        return showError(input, message);
    }
    return showSuccess(input);
}

function TextCount(input, message) {
    if (input.value.length === 0) {
        return showError(input, message);
    }
    return showSuccess(input);
}

function TableRowCount(input, message) {
    console.log("input.children.length ", input.children.length)
    if (input.children.length === 0) {
        return showError(input, message);
    }
    return showSuccess(input);
}

function DateValidate(input, requiredMsg, invalidMsg) {
    let d1 = new Date();
    if (input.valueAsDate instanceof Date) {
        if (input.valueAsDate >= d1) {
            return showSuccess(input);
        }
        return showError(input, invalidMsg);
    }
    return showError(input, requiredMsg);
}

function DateValidate2(input, input2, invalidMsg) {
    if (input.valueAsDate > input2.valueAsDate) {
        return showSuccess(input);
    }
    return showError(input, invalidMsg);
}

function SalaryValidate(input, message) {
    if (isNaN(input.valueAsNumber)) {
        return showError(input, message);
    }
    if (input.value < 0) {
        return showError(input, message);
    }
    return showSuccess(input);
}


function validateEmail(input, requiredMsg, invalidMsg) {
    // check if the value is not empty
    if (!hasValue(input, requiredMsg)) {
        return false;
    }
    // validate email format
    const emailRegex =
        /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

    const email = input.value.trim();
    if (email != "xxxx@xxx.com") {
        if (!emailRegex.test(email)) {
            return showError(input, invalidMsg);
        }
    }
    return true;
}



/*
form.addEventListener("submit", function(event) {
    // stop form submission
    event.preventDefault();

    // validate the form
    let nameValid = hasValue(form.elements["name"], NAME_REQUIRED);
    let emailValid = validateEmail(form.elements["email"], EMAIL_REQUIRED, EMAIL_INVALID);
    // if valid, submit the form.
    if (nameValid && emailValid) {
        alert("Demo only. No form was posted.");
    }
});
*/
function validaCantidateForm() {
    const form = document.getElementById('EmpresaCandidateOportunidad');

    let nameValid = hasValue(form.elements["name"], NAME_REQUIRED);
    let descriptionValid = TextCount(form.elements["description"], DESCRIPTION_REQUIRED);
    // nnueva funcion para validad los cargos
    // let miscategoryValid = TableRowCount(form.querySelector(`#mis_categ_ids_table tbody`), MIS_CATEG_IDS_REQUIRED);
    // let priorityValid = hasValue(form.elements["priority"], DESCRIPTION_REQUIRED);
    let emailValid = validateEmail(form.elements["email_from"], EMAIL_REQUIRED, EMAIL_INVALID);
    let date_openValid = DateValidate(form.elements["date_open"], DATE_REQUIRED, DATE_INVALID);
    let date_closeValid = DateValidate(form.elements["date_closed"], DATE_REQUIRED, DATE_INVALID);
    let date_betweenValid = DateValidate2(form.elements["date_closed"], form.elements["date_open"], DATE_INVALID);
    let cityValid = hasValue(form.elements["city"], CITY_REQUIRED);
    let salaryValid = SalaryValidate(form.elements["salary_proposed"], SALARY_REQUIRED);

    return nameValid && descriptionValid && emailValid && date_openValid && date_closeValid && date_betweenValid && cityValid && salaryValid;

}


function searchInObject(object, searchKey, searchValue) {
    for (var i in object) {
        if (object[i][searchKey] == searchValue) {
            return [i, object[i].name];
        };
    };
};

function _DelMisCat() {
    //console.log("Entre....")
    if (event.target.name === "CAT") {
        //console.log("Entre....CAT")
        //var div = event.srcElement.id
        var res_partner_category_id = event.srcElement.id;
        //console.log("Entre...event.srcElement ", event.srcElement);
        //console.log("Entre...this ", this);

        //console.log("Entre....res_partner_category_id ", res_partner_category_id);
        var a = document.getElementsByName("x_categ_dicts")[0].value;
        a = a.replaceAll("'", '"');
        var j = JSON.parse(a);

        // Find the whole record
        var n = searchInObject(j, "res_partner_category_id", res_partner_category_id);
        //console.log("_DelMisCat() Entre....n ", n);
        //console.log("_DelMisCat() antes-j ", j);
        // Delete selected record on JSON
        delete j[n[0]];
        //console.log("_DelMisCat() despues-j ", j);
        //console.log("_DelMisCat() n[0] ", n[0]);
        //console.log("_DelMisCat() n[1] ", n[1]);

        //let element = document.getElementById(n[1])

        let element = document.querySelector(`#mis_categ_ids_table tbody tr[id$="${n[1]}"]`);


        //console.log("_DelMisCat() element ", element);
        // Delete selected record on HTML
        element.remove();
        //console.log("Borrado HTML ");
        // Reindex
        j = Object.keys(j).map(key => j[key]);
        //console.log("Reindex j ", j);
        //console.log("JSON.stringify(j) ", JSON.stringify(j));
        document.getElementsByName("x_categ_dicts")[0].value = JSON.stringify(j);
        //console.log("j ", j);

        //_AddRowTableTotCat(res_partner_category_id, n[1]);

    };
};

function _AddMisCat() {
    //console.log("Add....");
    //console.log(this);
    var div = event.srcElement.id;
    var res_partner_category_id = event.srcElement.id;

    if (event.target.name === "CATTOT") {
        //console.log("Add CATTOT....");
        //console.log("Add....res_partner_category_id ", res_partner_category_id);

        let a = document.getElementsByName("x_categ_Totals")[0].value;
        a = a.replaceAll("'", '"');
        let j = JSON.parse(a);

        // Find the whole record
        let n = searchInObject(j, "res_partner_category_id", res_partner_category_id);
        //console.log("res_partner_category_id.... ", res_partner_category_id);
        //console.log("Entre....n ", n);
        //console.log("antes-j ", j);
        // Delete selected record
        //delete j[n[0]];
        //console.log("despues-j ", j);
        const element = document.getElementById(n[1]);
        //element.remove();
        //console.log("elemento borrado ", n);
        if (n[1]) {
            if (!document.querySelector(`#mis_categ_ids_table tbody tr[id$="${n[1]}"]`)) {
                //console.log("Adiciona HTML ", n);
                _AddRowTableMisCat(res_partner_category_id, n[1]);
            };
        };


    };
};

function _AddRowTableMisCat(_id, _name) {
    //let tableRef = document.getElementById("mis_categ_ids_table");
    console.log("_AddRowTableMisCat (_id,_name)", _id, _name)
    let tableRef = document.querySelector("#mis_categ_ids_table tbody");
    let _row = `<tr id="${_name}" category_id="${_id}"><td align="left">${_name}<a href="#" id=${_id} onclick="_DelMisCat(this)" name="CAT" class="fa fa-trash" title="Delete" aria-label="Delete"></a></td></tr>`;
    tableRef.innerHTML += _row;
    ////var a = document.getElementsByName("x_categ_dicts")[0].value;
    ////a = a.replaceAll("'", '"');
    ////var j = JSON.parse(a);
    ////let jr = `{"name": "${_name}", "partner_id": 0, "candidate_vacant_id": 0, "res_partner_category_id": ${_id}}`;
    //jr = JSON.parse(jr)
    ////jr = JSON.parse(jr);
    //console.log("Json row add ", jr);
    ////j.push(jr);
    // Reindex
    //console.log("Json row Added ", j);
    ////j = Object.keys(j).map(key => j[key]);
    ////document.getElementsByName("x_categ_dicts")[0].value = JSON.stringify(j);

};


function _AddRowTableTotCat(_id, _name) {
    //let tableRef = document.getElementById("mis_categ_ids_table");
    let tableRef = document.querySelector("#categ_ids_table tbody");

    if (!querySelector(`#mis_categ_ids_table tbody tr[id$="${_id}"]`)) {

        let _row = `<tr id="${_name}" category_id="${_id}"><td align="left">${_name}<a href="#" id=${_id} onclick="_AddMisCat(this)" name="CATTOT" class="fa fa-plus-square" title="Delete" aria-label="Delete"></a></td></tr>`;
        tableRef.innerHTML += _row;
    };

    var a = document.getElementsByName("x_categ_dicts")[0].value;
    a = a.replaceAll("'", '"');
    var j = JSON.parse(a);

    if (!searchInObject(j, "res_partner_category_id", _id)) {

        let jr = `{"name": "${_name}", "partner_id": 0, "candidate_vacant_id": 0, "res_partner_category_id": ${_id}}`;
        //jr = JSON.parse(jr)
        jr = JSON.parse(jr);
        //console.log("Json row add ", jr);
        j.push(jr);
        // Reindex
        //console.log("Json row Added ", j);
        j = Object.keys(j).map(key => j[key]);
        document.getElementsByName("x_categ_dicts")[0].value = JSON.stringify(j);

    };


};

function FilterJson(object, searchKey, searchValue) {
    let final = []
    for (var i in object) {
        if (object[i][searchKey] == searchValue) {
            if (!final.includes(object[i]["name_skill"])) {
                final.push(object[i]);
            };

        };
    };
    return final;
};


function clearChildren(parent_id) {

    var parent = document.getElementById(parent_id);
    var childArray = parent.children;
    var cL = childArray.length;
    console.log("Clean Chidren ", parent_id, cL);
    while (cL > 0) {
        cL--;
        parent.removeChild(childArray[cL]);

    };
};

function _LVFillSkillType() {

    let a = document.getElementsByName("skill_Total")[0].value;
    a = a.replaceAll("'", '"');
    a = JSON.parse(a);
    let A_skill_type = [...new Set(a.map(x => x.name_type))];
    let A_skill = [];

    //clearChildren("skilltypeDL");
    clearChildren("skillDL");
    console.log("Llenando skilltypeDL");

    var parent = document.getElementById("skilltypeDL");
    var childArray = parent.children;
    var cL = childArray.length;
    // console.log("cL ", cL);
    if (cL == 0) { // Aun tiene registros
        //if (!document.getElementsByName("addskilltype")[0].value) {
        let l = document.getElementById("skilltypeDL");
        for (var i in A_skill_type) {
            let opt = document.createElement("option");
            opt.setAttribute("value", A_skill_type[i]);
            l.appendChild(opt);
        }
        //}
    };
};

function _LVFillSkill() {

    let a = document.getElementsByName("skill_Total")[0].value;
    a = a.replaceAll("'", '"');
    a = JSON.parse(a);
    let A_skill_type = [...new Set(a.map(x => x.name_type))];
    let A_skill = [];

    let S_skill_type = document.getElementsByName("addskilltype")[0].value;
    console.log("S_skill_type selected ", S_skill_type);

    // Clean datalist 
    clearChildren("skillDL");
    if (S_skill_type) {
        console.log("Llena lita skillDL");
        A_skill = FilterJson(a, "name_type", S_skill_type);
        A_skill = [...new Set(A_skill.map(x => x.name_skill))];
        let l = document.getElementById("skillDL");
        for (var i in A_skill) {
            let opt = document.createElement("option");
            opt.setAttribute("value", A_skill[i]);
            l.appendChild(opt);
        };
    } else {
        let l = document.getElementById("skillDL");

    }
};


function _LVFillSkillLevel() {

    let a = document.getElementsByName("skill_Total")[0].value;
    a = a.replaceAll("'", '"');
    a = JSON.parse(a);
    let A_skill_type = [...new Set(a.map(x => x.name_type))];
    let S_skill_type = [];
    let A_skill = [];

    S_skill_type = document.getElementsByName("addskilltype")[0].value;
    S_skill = document.getElementsByName("addskill")[0].value;
    console.log("S_skill selected ", S_skill);

    // Clean datalist 
    clearChildren("skillLevelDL");
    console.log("S_skill_type ", S_skill_type);
    console.log("S_skill ", S_skill);
    if (S_skill) {
        console.log("Llena lita skillLevelDL");
        A_skill = FilterJson(a, "name_type", S_skill_type);
        A_skill = FilterJson(A_skill, "name_skill", S_skill);
        A_skill = [...new Set(A_skill.map(x => x.name_level))];
        let l = document.getElementById("skillLevelDL");
        for (var i in A_skill) {
            let opt = document.createElement("option");
            opt.setAttribute("value", A_skill[i]);
            l.appendChild(opt);
        };
    } else {
        let l = document.getElementById("skillDL");

    }
};

function _AddSkill() {

    let S_skill_type = document.getElementsByName("addskilltype")[0].value;
    let S_skill = document.getElementsByName("addskill")[0].value;
    let S_skilllevel = document.getElementsByName("addskilllevel")[0].value;


    if (!document.querySelector(`#skills_table tbody tr[id$="${S_skill}"]`)) {

        let a = document.getElementsByName("skill_Total")[0].value;
        a = a.replaceAll("'", '"');
        a = JSON.parse(a);
        let progress = 0
        let I_skill_type = "";
        let I_skill = "";
        let I_skilllevel = "";
        for (var i in a) {
            if (a[i].name_type == S_skill_type) {
                if (a[i].name_skill == S_skill) {
                    if (a[i].name_level == S_skilllevel) {
                        progress = a[i].level_progress;
                        I_skill_type = a[i].type_id;
                        I_skill = a[i].skill_id;
                        I_skilllevel = a[i].level_id;
                        //console.log("a[i] ", a[i]);
                    }

                }

            };

        };

        //console.log("progress ", progress);

        let tableRef = document.querySelector(`#skills_table tbody`);
        //let _row = `<tr id="${S_skill}"><td><span>${S_skill_type}</span></td><td><span>${S_skill}</span></td><td><span>${S_skilllevel}</span></td><td><div class="progress"><div class="progress-bar o_rating_progressbar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="50" style="width:50%;"><span class="px-2 text-warning">${progress}</span></div></div></td><td></div><a t-attf-href="#" class="fa fa-trash " t-attf-id="${S_skill}" t-attf-onclick="_DelMisSkill(this)" t-attf-name="SKILL"><i class="fa"></i></a></td></tr>`;
        // let _row = `<tr id="${S_skill}"><td><span>${S_skill_type}</span></td><td><span>${S_skill}</span></td><td><span>${S_skilllevel}</span></td><td><div class="progress"><div class="progress-bar o_rating_progressbar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${progress}" style="width:${progress}%;"><span class="px-2 text-warning">${progress}</span></div></div></td><td></div><a href="#" class="fa fa-trash " id="${S_skill}" onclick="_DelMisSkill(this)" name="SKILL"><i class="fa"></i></a></td></tr>`;
        let _row = `<tr skill_type_id="${I_skill_type}" skill_type_name="${S_skill_type}"  
        skill_id="${I_skill}"  skill_name="${S_skill}"
        skill_level_id="${I_skilllevel}"  skill_level_name="${S_skilllevel}" 
        id="${S_skill}"
        ><td>${S_skill_type}</td><td>${S_skill}</td><td>${S_skilllevel}</td><td><div class="progress"><div class="progress-bar o_rating_progressbar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${progress}" style="width:${progress}%;"><span class="px-2 text-warning">${progress}</span></div></div></td><td></div><a href="#" class="fa fa-trash " id="${S_skill}" onclick="_DelMisSkill(this)" name="SKILL"><i class="fa"></i></a></td></tr>`;

        //console.log(_row);
        tableRef.innerHTML += _row;

    };

}

function _DelMisSkill() {
    console.log("Entro.._DelMisSkill");
    if (event.target.name === "SKILL") {
        console.log("Entro..SKILL");
        console.log("event.srcElement..", event.srcElement);
        var id = event.srcElement.id;
        console.log("Entro..i", id);
        let element = document.querySelector(`#skills_table tbody tr[id$="${id}"]`);
        element.remove();
    };
};

function checkFileSize(evt) {
    let field = evt.srcElement;
    let file = field.files[0];

    // check the file size and use the setCustomValidity function
    // to indicate whether there is an error
    if (file.size > 500) {
        field.setCustomValidity("The file is too large");

    } else {
        field.setCustomValidity("");
    }
};


function _CategToJson(input) {
    const table = input;
    // document.querySelector('#mis_categ_ids_table tbody');
    //console.logs("table..", table);
    const rows = [...table.rows]
    const props = [...rows[0].attributes].map(a => { return a.name })

    const filas = [...rows].map(r => {
        const entries = [...r.attributes].map((c, i) => {
            return [props[i], c.value];

        });
        return Object.fromEntries(entries);
    });

    return JSON.stringify(filas);
};

function _SkillToJson(input) {
    const table = input
        // document.querySelector('#skills_table tbody');
    const rows = [...table.rows].map(r => {
        const entries = [...r.cells].map((c) => {
            return (c.textContent.trim())
        });
        return entries;
    })

    return JSON.stringify(rows);
};


/*

function _CategToJson(input) {
    const table = input
        // document.querySelector('#mis_categ_ids_table tbody');
    const rows = [...table.rows].map(r => { return (r.id) });
    //rows
    return JSON.stringify(rows);
};


function _SkillToJson(input) {
    const table = input
        // document.querySelector('#skills_table tbody');
    const rows = [...table.rows].map(r => {
        const entries = [...r.cells].map((c) => {
            return (c.textContent.trim())
        });
        return Object.fromEntries(Object.entries(entries));
    })

    return JSON.stringify(rows);
};

*/