const NAME_REQUIRED = "Ingresar el nombre del cargo";
const NAME_PERSONA = "Ingresar el nombre";
const EMAIL_REQUIRED = "Ingrese un email";
const EMAIL_INVALID = "Ingrese un email correcto";

const DESCRIPTION_REQUIRED = "Por favor ingrese una descripción del cargo..";
const FUNCTION_REQUIRED = "Por favor ingrese la función del cargo..";
const ACHIEVEMENTS_REQUIRED = "Por favor ingrese los logros del cargo..";

const COMPANY_REQUIRED = "Por favor ingrese la compañía..";
const MIS_CATEG_IDS_REQUIRED = "Se requiere al menos un cargo";

const DATE_INVALID = "Fecha invalida";
const DATE_REQUIRED = "Fecha requerida";

const CITY_REQUIRED = "Ingresar ciudad del cargo";
const SALARY_REQUIRED = "Salario invalido";

const VAT_PERSONA = "Es obligatorio el documento de identidad";
const PHONE_PERSONA = "Es obligatorio el numero de celular";
const STREET_PERSONA = "Es obligatorio el numero de celular";

const PROFILE_REQUIRED = "Se requiere de su perfil";
const COVER_REQUIRED = "Ingrese la carta de presentacion";

// ****


Date.prototype.toDateInputValue = function() {
    var datestring = this.getFullYear() + "-" + ("0" + (this.getMonth())).slice(-2) + "-" + ("0" + this.getDate()).slice(-2);
    return datestring;
};
Date.prototype.toDateInputValueMonth = function() {
    var datestring = this.getFullYear() + "-" + ("0" + (this.getMonth() + 1)).slice(-2) + "-" + ("0" + this.getDate()).slice(-2);
    return datestring;
};


window.addEventListener("load", e => {
    // console.log("Evento Hoja de Vida");
    let theform = document.getElementById("EmpresaHojadeVida");
    //let descriptioncount = document.getElementById("description");
    //let countdescription = document.getElementById("countdescription");

    let addskilltype = document.getElementById("addskilltype");
    let addskill = document.getElementById("addskill");
    let addskilllevel = document.getElementById("addskilllevel");
    let btnaddskill = document.getElementById("btnaddskill");
    //let btnaddCateg = document.getElementById("btnaddsCateg");



    // Inicio de captura de evento de experiencia
    let AdicionaJob = document.getElementById("AdicionaJob");
    let AdicionaEst = document.getElementById("AdicionaEst");
    let PopUpExp_Cancel = document.getElementById("PopUpExp_Cancel");
    let PopUpEst_Cancel = document.getElementById("PopUpEst_Cancel");
    let PopUpExp_Confirm = document.getElementById("PopUpExp_Confirm");
    let PopUpEst_Confirm = document.getElementById("PopUpEst_Confirm");

    // PopUp Form para validar
    let Expform = document.getElementById("PopUpExpForm");
    let PopUpExp_date_end = document.getElementById("PopUpExp_date_end");
    let PopUpExp_date_start = document.getElementById("PopUpExp_date_start");

    //let datestring = this.getFullYear() + "-" + ("0" + (this.getMonth())).slice(-2) + "-" + ("0" + this.getDate()).slice(-2);
    let d = new Date(Date.now()),
        month = '' + ("0" + (d.getMonth())).slice(-2),
        day = '' + ("0" + d.getDate()).slice(-2),
        year = d.getFullYear()


    PopUpExp_date_start.min = [year - 50, month, day].join('-')
    PopUpExp_date_start.max = [year, month, day].join('-')
    PopUpExp_date_end.min = [year - 50, month, day].join('-')
    PopUpExp_date_end.max = [year, month, day].join('-')



    PopUpExp_Cancel.addEventListener("click", e => {
        document.getElementById("PopUpExp").style.display = "none";
        document.getElementById("AdicionaJob").focus();
        _ClearRowExp_table()

    });

    PopUpEst_Cancel.addEventListener("click", e => {
        document.getElementById("PopUpEst").style.display = "none";
        document.getElementById("AdicionaEst").focus();
        _ClearRowEst_table()
    });

    PopUpEst_Confirm.addEventListener("click", e => {
        const result = validateESTForm();
        //console.log("Validar los datos de la nueva educacion", result);
        if (!result) {
            document.getElementById("AdicionaEst").focus();
        } else {
            document.getElementById("PopUpEst").style.display = "none";
            document.getElementById("AdicionaEst").focus();
            // console.log("Insertar el registro en la tabla de educacion");
            _AddRowEst_table();
            _ClearRowEst_table();


        }
    });

    PopUpExp_Confirm.addEventListener("click", e => {
        const result = validateEXPForm();
        // console.log("Validar los datos de la nueva experiencia", result);
        if (!result) {
            document.getElementById("AdicionaJob").focus();
        } else {
            document.getElementById("PopUpExp").style.display = "none";
            document.getElementById("AdicionaJob").focus();
            // console.log("Insertar el registro en la tabla de de experiencia");
            _AddRowExp_table();
            _ClearRowExp_table();


        }
    });

    //clearChildren("skilltypeDL");
    // console.log("windows HV load _LVFillSkillType");
    _LVFillSkillType();
    // console.log("windows HV FIN _LVFillSkillType");
    //_SkillLV();
    const SkillJson = [];
    const CatJson = [];
    // console.log("windows HV FIN _LVFillSkillType");
    _LVFillCategDL();

    // Cargar la foto
    document.getElementById("x_photo").attributes.src.value = "data:image/png;base64," + document.getElementsByName("x_photo")[0].value
        // document.getElementById("x_photo").attributes.src.value = document.getElementsByName("x_photo")[0].value

    AdicionaJob.addEventListener("click", e => {
        console.log(" Evento adiciona experiencia ");
        if (document.getElementById("PopUpExp").style.display == "none") {
            document.getElementById("PopUpExp").style.display = "block";
        } else {
            document.getElementById("PopUpExp").style.display = "none";
        }


    });

    AdicionaEst.addEventListener("click", e => {
        //console.log(" Evento adiciona estudio ");
        if (document.getElementById("PopUpEst").style.display == "none") {
            document.getElementById("PopUpEst").style.display = "block";
        } else {
            document.getElementById("PopUpEst").style.display = "none";
        }


    });
    addskilltype.addEventListener("input", e => {
        //console.log(" Evento HV input on addskilltype ");
        _LVFillSkill();
        _LVFillSkillLevel();
    });


    btnaddskill.addEventListener('click', e => {

        let l = document.getElementById('addskilllevel')
        if (l.value.length > 0) {
            //console.log(" Evento click on btnaddskill ");
            _AddSkill();

            btnaddskill.setAttribute('disabled', 'true');
            document.getElementById("addskill").value = [];
            document.getElementById("addskilllevel").value = [];
            document.getElementById("addskilltype").value = [];
        } else {
            e.preventDefault();
        }

    });


    const status = document.getElementById('status');
    const output = document.getElementById('x_photo');
    document.getElementById('file-selector').addEventListener('change', event => {
        output.innerHTML = '';
        for (const file of event.target.files) {
            const li = document.createElement('li');
            const name = file.name ? file.name : 'NOT SUPPORTED';
            const type = file.type ? file.type : 'NOT SUPPORTED';
            const size = file.size ? file.size : 'NOT SUPPORTED';
            li.textContent = `name: ${name}, type: ${type}, size: ${size}`;
            output.appendChild(li);
        }
        // console.log("leer el archivo");
        const file = event.target.files[0];
        // console.log("event.target.files[0]", event.target.files[0])
        if (!file.type) {
            status.textContent = 'Error: El tipo de archivo no cumple con lo solicitado';
            return;
        }
        if (!file.type.match('image.*')) {
            status.textContent = 'Error: El archivo seleccionado no parece ser una imagen'
            return;
        }
        const reader = new FileReader();
        reader.addEventListener('load', event => {
            output.src = event.target.result;
        });
        reader.readAsDataURL(file);
        //console.log("otro..", otro)
        //console.log("file readed.. ", file)
        //console.log("output ", output)
        //console.log("reader ", reader)

        //document.getElementsByName("x_photo")[0].value = output.src

        document.getElementsByName("x_photo")[0].value = document.getElementById("x_photo").src

    });

    /*
        btnaddCateg.addEventListener('click', e => {
            console.log("Entro en btnaddCateg")
                //let theform = document.getElementById("EmpresaHojadeVida");
                //theform.addEventListener("submit", e => {
                //    e.preventDefault();
                //});

            let CategJson = _CategToJson(document.querySelector('#categ_table tbody'));
            let long = CategJson.length
            console.log("longitud de la lista de categoria ", long)
            if (long > 0) {
                CategJson = JSON.parse(CategJson);
            } else {
                CategJson = []
            }
            console.log("CategJson ", CategJson)
            let x = document.getElementById("CategDL").selectedOptions;
            console.log("x ", x, x.length)
            for (i = 0; i <= x.length - 1; i++) {
                let val_id = x[i].attributes[1].value
                let val_name = x[i].attributes[0].value
                console.log("CategJson ", CategJson)

                let enc = searchInObject(CategJson, "res_partner_category_id", val_id)
                    //    console.log("Search ", enc)
                let tableRef = document.querySelector(`#categ_table tbody`);
                //    console.log(val_id)
                if (!enc) {
                    console.log("Agregó categoria....")

                    let _row = `<tr class="badge badge-pill" res_partner_category_id="${val_id}" name="${val_name}">
                                    <td>
                                        <span res_partner_category_id="${val_id}" name="${val_name}">${val_name}</span>
                                    </td>
                                        <td>
                                        <div class="btn btn-sm btn-link" cat_id="${val_id}"></div>
                                        <a href="#" class="fa fa-fw fa-remove"  id="${val_id}" onclick="_DelMisCateg(this)" name="CATEG"><i class="fa"></i></a>
                                        </td>
                                    </tr>`
                    tableRef.innerHTML += _row;
                } else {
                    console.log("No se agrega categoria....")
                }

            }
            //alert("Parar para ver los selected");
            // alert()
        });
    */
    addskilltype.addEventListener('click', e => {
        e.target.value = '';
        //console.log(" Evento click on addskilltype ");
        document.getElementById("addskill").value = '';
        document.getElementById("addskilllevel").value = '';
        _LVFillSkillType();
        btnaddskill.setAttribute('disabled', 'true');
    });

    addskilltype.addEventListener('click', e => {
        e.target.select();
        //console.log(" Evento click2 on addskilltype ");
        document.getElementById("addskill").value = '';
        document.getElementById("addskilllevel").value = '';
        //_SkillLV();
        _LVFillSkillLevel();
        btnaddskill.setAttribute('disabled', 'true');
    });

    addskill.addEventListener('click', e => {
        e.target.value = ''
            //console.log(" Evento click on addskill ");
        document.getElementById("addskilllevel").value = '';
        _LVFillSkillLevel();
        btnaddskill.setAttribute('disabled', 'true');

    });

    /* addskill.addEventListener('click', e => {
        e.target.select()
        console.log(" Evento click2 on addskill ");
        document.getElementById("addskilllevel").value = '';
        _LVFillSkillLevel();
    });

*/
    addskilllevel.addEventListener('click', e => {
        e.target.value = ''
            //console.log(" Evento click on addskilllevel ");
        _LVFillSkillLevel();
        btnaddskill.setAttribute('disabled', 'true');
    });


    addskilllevel.addEventListener('click', e => {
        e.target.select()
            //console.log("e.target.select() ", e.target.select())
            //console.log(" Evento click2 on addskilllevel ");
        const input = document.querySelector('addskilllevel')
            //console.log("input ", input)
            //input.onchange = (e) => {
            //    console.log("Change ", e.target.value)
            //}

        //_LVFillSkillLevel(); 
        btnaddskill.removeAttribute('disabled');

    });


    // boton par adicionar un skill btnaddskill


    addskilllevel.addEventListener('onchange', e => {
        e.target.select()
            //console.log("e.target.select() ", e.target.select())
            //console.log(" Evento change on addskilllevel ");

        //_LVFillSkillLevel(); 
        btnaddskill.removeAttribute('disabled');

    });


    // TODO: prevent the form from being auto-submitted when the user  
    // clicks the Submit button or types Enter in a field
    theform.addEventListener("submit", e => {
        //e.preventDefault();
        //console.log("submit HV button");
        //alert("Se va a avalidar submmit")

        const result = validaCantidateForm()

        //result = 1;
        //console.log(" validaCantidateForm HV ", result);


        //e.preventDefault();
        //alert("Antes de !result")
        if (!result) {
            // stop form submission
            //alert("No se cumple con la validacion")
            e.preventDefault();
        } else {
            // prepare information about array
            const CatJson = JSON.stringify(_CategToJson(document.querySelector('#categ_table tbody')));
            const SkillJson = JSON.stringify(_CategToJson(document.querySelector('#skills_table tbody')));
            const x_estudios_ids = JSON.stringify(_CategToJson(document.querySelector('#Est_table tbody')));
            const x_experiencia_ids = JSON.stringify(_CategToJson(document.querySelector('#Exp_table tbody')));
            document.getElementsByName("x_categ_dicts")[0].value = CatJson;
            document.getElementsByName("x_skill_ids")[0].value = SkillJson;

            document.getElementsByName("x_estudios_ids")[0].value = x_estudios_ids;
            document.getElementsByName("x_experiencia_ids")[0].value = x_experiencia_ids;
            document.getElementsByName("x_photo")[0].value = document.getElementById("x_photo").src

            //alert("This alert will never be shown.");
            //e.preventDefault();

        }

    })

});

class FormEventListener {
    constructor(formElem) {
        this.formElem = formElem;
    }

    // TODO: define the handleEvent function to make this object an event handler
}


function _AddCateg() {
    let theform = document.getElementById("EmpresaHojadeVida");
    //theform.addEventListener("submit", e => {
    //    e.preventDefault();
    //});
    let x = document.getElementById("CategDL").selectedOptions;
    for (var i in x) {
        console.log("Selected ", i.value);
    }
    //alert("Parar para ver los selected");
};



// show a message with a type of the input
function showMessage(input, message, type) {
    // get the small element and set the message
    const msg = input.parentNode.querySelector("small");
    msg.innerText = message;
    // update the class for the input
    input.className = type ? "form-control success" : "form-control error";
    return type;
}

function showError(input, message) {
    //console.log("Entro showError ")
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
    //console.log("input.children.length ", input.children.length)
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
    //console.log("input ", input)
    //console.log("input2 ", input2)
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


function validaCantidateForm() {
    const form = document.getElementById('EmpresaHojadeVida');

    let nameValid = hasValue(form.elements["name"], NAME_PERSONA);
    // nnueva funcion para validad los cargos
    let emailValid = validateEmail(form.elements["email"], EMAIL_REQUIRED, EMAIL_INVALID);
    let birthday = hasValue(form.elements["birthday"], DATE_INVALID);
    let vat = hasValue(form.elements["vat"], VAT_PERSONA);
    let phone = hasValue(form.elements["phone"], PHONE_PERSONA);
    let street = hasValue(form.elements["street"], STREET_PERSONA);

    let cityValid = hasValue(form.elements["city"], CITY_REQUIRED);
    let salaryValid = SalaryValidate(form.elements["salary"], SALARY_REQUIRED);

    let profile = TextCount(form.elements["profile"], PROFILE_REQUIRED);
    let cover = TextCount(form.elements["cover"], COVER_REQUIRED);

    return nameValid && emailValid && birthday && vat && phone && street && cityValid && salaryValid && profile && cover;

}

function validateEXPForm() {


    const form = document.getElementById('PopUpExpForm');

    let JobValid = hasValue(form.elements["PopUpExp_job_title"], NAME_REQUIRED);
    let nameValid = hasValue(form.elements["PopUpExp_name"], COMPANY_REQUIRED);
    let date_betweenValid = DateValidate2(form.elements["PopUpExp_date_end"], form.elements["PopUpExp_date_start"], DATE_INVALID);
    let functionValid = TextCount(form.elements["PopUpExp_functions"], FUNCTION_REQUIRED);
    let achievementsValid = TextCount(form.elements["PopUpExp_achievements"], ACHIEVEMENTS_REQUIRED);

    return JobValid && nameValid && date_betweenValid && functionValid && achievementsValid;

}

function validateESTForm() {


    const form = document.getElementById('EmpresaHojadeVida');

    let EduValid = hasValue(form.elements["PopUpEst_edu_title"], NAME_REQUIRED);
    let nameValid = hasValue(form.elements["PopUpEst_name"], COMPANY_REQUIRED);
    let date_betweenValid = DateValidate2(form.elements["PopUpEst_date_end"], form.elements["PopUpEst_date_start"], DATE_INVALID);

    return EduValid && nameValid && date_betweenValid;

}



function searchInObject(object, searchKey, searchValue) {
    //console.log("object ", object)
    //console.log("searchKey ", searchKey)
    //console.log("searchValue ", searchValue)


    for (var i in object) {
        //console.log("obj searchInObject ", object[i][searchKey])
        if (object[i][searchKey] == searchValue) {
            return [i, object[i].name];
        };
    };
    //alert("")
};

function _DelMisCat() {
    //console.log("Entre....")
    if (event.target.name === "CAT") {
        //console.log("Entre....CAT")
        //var div = event.srcElement.id
        var res_partner_category_id = event.srcElement.id;

        var a = document.getElementsByName("x_categ_dicts")[0].value;
        a = a.replaceAll("'", '"');
        var j = JSON.parse(a);

        // Find the whole record
        var n = searchInObject(j, "res_partner_category_id", res_partner_category_id);
        delete j[n[0]];

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
    var div = event.srcElement.id;
    var res_partner_category_id = event.srcElement.id;
    //console.log("entro en _AddMisCat....");
    if (event.target.name === "CATTOT") {
        //console.log("Add CATTOT....");
        //console.log("Add....res_partner_category_id ", res_partner_category_id);

        let a = document.getElementsByName("x_categ_Totals")[0].value;
        a = a.replaceAll("'", '"');
        let j = JSON.parse(a);

        // Find the whole record
        let n = searchInObject(j, "res_partner_category_id", res_partner_category_id);
        const element = document.getElementById(n[1]);
        if (n[1]) {
            if (!document.querySelector(`#mis_categ_ids_table tbody tr[id$="${n[1]}"]`)) {
                _AddRowTableMisCat(res_partner_category_id, n[1]);
            };
        };


    };
};

function _AddRowTableMisCat(_id, _name) {
    //console.log("_AddRowTableMisCat (_id,_name)", _id, _name)
    let tableRef = document.querySelector("#mis_categ_ids_table tbody");
    let _row = `<tr id="${_name}" category_id="${_id}"><td align="left">${_name}<a href="#" id=${_id} onclick="_DelMisCat(this)" name="CAT" class="fa fa-trash" title="Delete" aria-label="Delete"></a></td></tr>`;
    tableRef.innerHTML += _row;
};

function _AddRowExp_table() {

    let id = document.getElementsByName("PopUpExp_indice")[0].value
        //console.log("_AddRowExp_table ", id)
    if (id == '') {

        let tableRef = document.querySelector("#Exp_table tbody");
        let PopUpExp_job_title = document.getElementsByName("PopUpExp_job_title")[0].value;
        let PopUpExp_name = document.getElementsByName("PopUpExp_name")[0].value;
        let PopUpExp_date_start = document.getElementsByName("PopUpExp_date_start")[0].value;
        let PopUpExp_date_end = document.getElementsByName("PopUpExp_date_end")[0].value;
        let PopUpExp_functions = document.getElementsByName("PopUpExp_functions")[0].value;
        let PopUpExp_achievements = document.getElementsByName("PopUpExp_achievements")[0].value;

        // Encontrar el indice maximo
        let row = [...tableRef.rows]
        var max = -1
        row.forEach((e) => {
            //console.log(e.attributes.PopUpExp_indice.value)
            if (!isNaN(e.attributes.PopUpExp_indice.value)) {
                if (e.attributes.PopUpExp_indice.value > max) {
                    max = e.attributes.PopUpExp_indice.value
                }
            }
        })

        let index = 1 + Number(max)

        let _row = `<tr PopUpExp_indice = "${index}" PopUpExp_job_id="-1" PopUpExp_job_title="${PopUpExp_job_title}" PopUpExp_name="${PopUpExp_name}" PopUpExp_date_start="${PopUpExp_date_start}" PopUpExp_date_end="${PopUpExp_date_end}"
        PopUpExp_functions="${PopUpExp_functions}"  PopUpExp_achievements="${PopUpExp_achievements}">
            <td>
            <span>${PopUpExp_job_title}</span>
            </td>
            <td>
            <span>${PopUpExp_name}</span>
            </td>
            <td>
            <span type="date">${PopUpExp_date_start}</span>
            </td>
            <td>
            <span type="date">${PopUpExp_date_end}</span>
            </td>
            <td>
            <div job_id="-1"></div>
            <a t-attf-href="#" t-att-PopUpExp_indice="${index}" class="fa fa-pencil" t-attf-onclick="_UpdateMisExp(this)" t-attf-name="EXP"><i class="fa"/></a>
            </td>
            <td>
            <a t-attf-href="#" class="fa fa-trash " t-att-PopUpExp_indice="${index}" t-att-job_id="-1" t-attf-onclick="_DelMisExp(this)" t-attf-name="EXP">
            <i class="fa"/>
            </a>
        </td>           
        </tr>`;
        tableRef.innerHTML += _row;

    } else {

        let element = document.querySelector(`#Exp_table tbody tr[PopUpExp_indice$="${id}"]`);
        element.attributes.popupexp_job_title.value = document.getElementsByName("PopUpExp_job_title")[0].value
        element.children[0].children[0].innerHTML = document.getElementsByName("PopUpExp_job_title")[0].value
        element.children[1].children[0].innerHTML = document.getElementsByName("PopUpExp_name")[0].value
        element.children[2].children[0].innerHTML = document.getElementsByName("PopUpExp_date_start")[0].value
        element.children[3].children[0].innerHTML = document.getElementsByName("PopUpExp_date_end")[0].value

        element.attributes.PopUpExp_name.value = document.getElementsByName("PopUpExp_name")[0].value
        element.attributes.PopUpExp_date_start.value = document.getElementsByName("PopUpExp_date_start")[0].value
        element.attributes.PopUpExp_date_end.value = document.getElementsByName("PopUpExp_date_end")[0].value

        element.attributes.PopUpExp_functions.value = document.getElementsByName("PopUpExp_functions")[0].value
        element.attributes.PopUpExp_achievements.value = document.getElementsByName("PopUpExp_achievements")[0].value
        element.attributes.PopUpExp_job_id.value = document.getElementsByName("PopUpExp_job_id")[0].value;
        element.attributes.PopUpExp_indice.value = document.getElementsByName("PopUpExp_indice")[0].value;
    }
    _ClearRowExp_table()
};


function _AddRowEst_table() {


    let id = document.getElementsByName("PopUpEst_indice")[0].value
        //console.log("_AddRowEst_table ", id)
    if (id == '') {
        //console.log("Se activa boton de adicionar estudio")
        let tableRef = document.querySelector("#Est_table tbody");
        let PopUpEst_edu_title = document.getElementsByName("PopUpEst_edu_title")[0].value;
        let PopUpEst_name = document.getElementsByName("PopUpEst_name")[0].value;
        let PopUpEst_date_start = document.getElementsByName("PopUpEst_date_start")[0].value;
        let PopUpEst_date_end = document.getElementsByName("PopUpEst_date_end")[0].value;
        //console.log("document.getElementsByName( ", document.getElementsByName("PopUpEst_edu_type")[0].value)

        //let PopUpEst_edu_type = document.getElementsByName("PopUpEst_edu_type")[0].value;
        let PopUpEst_edu_type = document.getElementsByName("PopUpEst_edu_type_sel")[0].value
            //console.log("PopUpEst_edu_type ", PopUpEst_edu_type)
        let PopUpEst_edu_id = '-1'

        // Encontrar el indice maximo
        let row = [...tableRef.rows]
        var max = -1
        row.forEach((e) => {
            //console.log(e.attributes.PopUpEst_indice.value)
            if (!isNaN(e.attributes.PopUpEst_indice.value)) {
                if (e.attributes.PopUpEst_indice.value > max) {
                    max = e.attributes.PopUpEst_indice.value
                }
            }
        })

        let index = 1 + Number(max)

        let _row = `<tr popupest_indice="${index}" PopUpEst_edu_id="${PopUpEst_edu_id}" popupest_name="${PopUpEst_name}" popupest_edu_title="${PopUpEst_edu_title}" popupest_date_start="${PopUpEst_date_start}" popupest_date_end="${PopUpEst_date_end}" popupest_edu_type="${PopUpEst_edu_type}">
            <td>
                <span>${PopUpEst_name}</span>
            </td>
            <td>
                <span>${PopUpEst_edu_title}</span>
            </td>
            <td>
                <span type="date">${PopUpEst_date_start}</span>
            </td>
            <td>
                <span type="date">${PopUpEst_date_end}</span>
            </td>
            <td>
                <a class="fa fa-pencil" href="#" popupest_indice="${index}" onclick="_UpdateMisEst(this)" name="EST"><i class="fa"></i></a>
            </td>
        <td>
            <a class="fa fa-trash " href="#" popupest_indice="${index}" popupest_edu_id="5" onclick="_DelMisEst(this)" name="EST">
                <i class="fa"></i>
            </a>
        </td>                                    
        </tr>`;
        tableRef.innerHTML += _row;
    } else {

        let element = document.querySelector(`#Est_table tbody tr[PopUpEst_indice$="${id}"]`);
        element.attributes.popupEst_edu_title.value = document.getElementsByName("PopUpEst_edu_title")[0].value
        element.children[0].children[0].innerHTML = document.getElementsByName("PopUpEst_name")[0].value
        element.children[1].children[0].innerHTML = document.getElementsByName("PopUpEst_edu_title")[0].value
        element.children[2].children[0].innerHTML = document.getElementsByName("PopUpEst_date_start")[0].value
        element.children[3].children[0].innerHTML = document.getElementsByName("PopUpEst_date_end")[0].value
            //element.children[4].children[0].innerHTML = document.getElementsByName("PopUpEst_edu_type")[0].value

        element.attributes.PopUpEst_name.value = document.getElementsByName("PopUpEst_name")[0].value
        element.attributes.PopUpEst_date_start.value = document.getElementsByName("PopUpEst_date_start")[0].value
        element.attributes.PopUpEst_date_end.value = document.getElementsByName("PopUpEst_date_end")[0].value
        element.attributes.popupEst_edu_type.value = document.getElementsByName("PopUpEst_edu_type")[0].value

        element.attributes.PopUpEst_edu_id.value = document.getElementsByName("PopUpEst_edu_id")[0].value;
        element.attributes.PopUpEst_indice.value = document.getElementsByName("PopUpEst_indice")[0].value;
    }
    _ClearRowEst_table()
};


function _ClearRowExp_table() {
    document.getElementsByName("PopUpExp_job_title")[0].value = '';
    document.getElementsByName("PopUpExp_name")[0].value = '';
    document.getElementsByName("PopUpExp_date_start")[0].value = '';
    document.getElementsByName("PopUpExp_date_end")[0].value = '';
    document.getElementsByName("PopUpExp_functions")[0].value = '';
    document.getElementsByName("PopUpExp_achievements")[0].value = '';
    document.getElementsByName("PopUpExp_job_id")[0].value = '-1';
    document.getElementsByName("PopUpExp_indice")[0].value = '';
};

function _ClearRowEst_table() {
    document.getElementsByName("PopUpEst_name")[0].value = '';
    document.getElementsByName("PopUpEst_edu_title")[0].value = '';
    document.getElementsByName("PopUpEst_edu_type")[0].value = '';
    document.getElementsByName("PopUpEst_date_start")[0].value = '';
    document.getElementsByName("PopUpEst_date_end")[0].value = '';

    document.getElementsByName("PopUpEst_edu_id")[0].value = '-1';
    document.getElementsByName("PopUpEst_indice")[0].value = '';
    //console.log("finalizó _ClearRowEst_table")
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
    //let parent_id = "skillLevelDL"
    var parent = document.getElementById(parent_id);
    if (parent.children.length > 0) {

        var childArray = parent.children;
        var cL = childArray.length;
        //console.log("Clean Chidren ", parent_id, cL);
        while (cL > 0) {
            cL--;
            parent.removeChild(childArray[cL]);

        };
    }
};

function _LVFillSkillType() {

    let a = document.getElementsByName("skill_Total")[0].value;
    a = a.replaceAll("'", '"');
    a = JSON.parse(a);
    let A_skill_type = [...new Set(a.map(x => x.name_type))];
    let A_skill = [];

    //clearChildren("skilltypeDL");
    clearChildren("skillDL");
    // console.log("Llenando skilltypeDL");

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
    //console.log("S_skill_type selected ", S_skill_type);

    // Clean datalist 
    clearChildren("skillDL");
    if (S_skill_type) {
        //console.log("Llena lita skillDL");
        A_skill = FilterJson(a, "name_type", S_skill_type);
        A_skill = [...new Set(A_skill.map(x => x.name_skill))];
        let l = document.getElementById("skillDL");
        l.innerHTML = "";
        for (var i in A_skill) {
            let opt = document.createElement("option");
            opt.setAttribute("value", A_skill[i]);
            l.appendChild(opt);
        };
    } else {
        let l = document.getElementById("skillDL");

    }
};

function clearSelectList(list) {
    // when length is 0, the evaluation will return false.
    while (list.options.length) {
        // continue to remove the first option until no options remain.
        list.remove(0);
    }
};

function _LVFillCategDL() {
    let a = document.getElementsByName("x_categ_Totals")[0].value;
    a = a.replaceAll("'", '"');
    a = JSON.parse(a);
    let A_name = [...new Set(a.map(x => x.name))];
    let A_ateg = [];

    /*
    let l = document.getElementById("CategDL");
    // Clean the list 
    clearSelectList(l);

    // Fill with the first record
    let opt = document.createElement("option");
    opt.innerHTML = "--Seleccione uno o mas cargos a adicionar--"
    opt.setAttribute("value", "");
    l.appendChild(opt);

    // Fill with the real records
    for (var i in a) {
        let opt = document.createElement("option");
        opt.setAttribute("value", a[i].name);
        opt.innerHTML = a[i].name
        opt.setAttribute("res_partner_category_id", a[i].res_partner_category_id)
        l.appendChild(opt);
    };
*/
    // Inicio de tabla para categoria
    for (var i in a) {

        // Preguntar aca si la categoria esta en mis-categorias
        let l = document.querySelector(`#categ_table tbody`)
        let exist = 0
        let ind = 0
        for (ind = 0; ind < l.children.length; ind++) {
            if (l.children[ind].attributes['res_partner_category_id'].value == a[i].res_partner_category_id) {
                exist = 1;
                // console.log("Categoria esta en mis-categorias", a[i].name)
                break;
            };
        }
        if (exist == 0) {
            let tableRef = document.querySelector(`#categia_table tbody`);
            let _row = `<tr res_partner_category_id="${a[i].res_partner_category_id}" name="${a[i].name}" >
            <td>
                <div class="btn btn-sm btn-link" res_partner_category_id="${a[i].res_partner_category_id}">
                    <a href="#" id="${a[i].res_partner_category_id}"  res_partner_category_id="${a[i].res_partner_category_id}" class="fa fa-fw fa-plus" onclick="_AddMisCateg(this)" name="CATEGTABLE" res_partner_category_name="${a[i].name}"></a>
    
                </div>
                <span> ${a[i].name}
                </span>            
            </td>
            </tr>`;

            //console.log(_row);
            tableRef.innerHTML += _row;

        }


    };
    // Fin de tabla para categoria
    // console.log("Finaliza _LVFillCategDL")
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
    //console.log("S_skill selected ", S_skill);

    // Clean datalist 
    clearChildren("skillLevelDL");
    //console.log("S_skill_type ", S_skill_type);
    //console.log("S_skill ", S_skill);
    if (S_skill.length > 0) {
        //console.log("Llena lita skillLevelDL");
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

        let tableRef = document.querySelector(`#skills_table tbody`);
        let _row = `<tr skill_type_id="${I_skill_type}" skill_type_name="${S_skill_type}"  
        skill_id="${I_skill}"  skill_name="${S_skill}"
        skill_level_id="${I_skilllevel}"  skill_level_name="${S_skilllevel}" 
        id="${S_skill}"
        ><td>${S_skill_type}</td><td>${S_skill}</td><td>${S_skilllevel}</td><td><div class="progress"><div class="progress-bar o_rating_progressbar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${progress}" style="width:${progress}%;"><span class="px-2 text-warning">${progress}</span></div></div></td><td></div><a href="#" class="fa fa-trash " id="${S_skill}" onclick="_DelMisSkill(this)" name="SKILL"><i class="fa"></i></a></td></tr>`;

        //console.log(_row);
        tableRef.innerHTML += _row;

    };

}

function _DelMisEst() {
    //console.log("Entro.._DelMisEst");
    if (event.target.name === "EST") {
        //console.log("Entro..EST");
        //console.log("event.srcElement..", event.srcElement);
        var id = event.srcElement.attributes.PopUpEst_indice.value;
        //console.log("Entro..i", id);
        let element = document.querySelector(`#Est_table tbody tr[PopUpEst_indice$="${id}"]`);
        element.remove();
    };
};

function _DelMisExp() {
    //console.log("Entro.._DelMisExp");
    if (event.target.name === "EXP") {
        //console.log("Entro..EXP");
        //console.log("event.srcElement..", event.srcElement);
        var id = event.srcElement.attributes.PopUpExp_indice.value;
        //console.log("Entro..i", id);
        let element = document.querySelector(`#Exp_table tbody tr[PopUpExp_indice$="${id}"]`);
        element.remove();
    };
};

function _UpdateMisExp() {
    //console.log("event.target.name ", event.target.name)
    if (event.target.name === "EXP") {
        //console.log("Entro..EXP");
        //console.log("event.srcElement..", event.srcElement);
        var id = event.srcElement.attributes.PopUpExp_indice.value;
        //console.log("Entro..i", id);
        let element = document.querySelector(`#Exp_table tbody tr[PopUpExp_indice$="${id}"]`);
        // Activar el PopUp
        document.getElementById("PopUpExp").style.display = "block";
        // document.getElementById("AdicionaJob").focus();

        document.getElementsByName("PopUpExp_job_title")[0].value = element.attributes.PopUpExp_job_title.value;
        document.getElementsByName("PopUpExp_name")[0].value = element.attributes.PopUpExp_name.value;
        document.getElementsByName("PopUpExp_date_start")[0].value = element.attributes.PopUpExp_date_start.value;
        document.getElementsByName("PopUpExp_date_end")[0].value = element.attributes.PopUpExp_date_end.value;
        document.getElementsByName("PopUpExp_functions")[0].value = element.attributes.PopUpExp_functions.value;
        document.getElementsByName("PopUpExp_achievements")[0].value = element.attributes.PopUpExp_achievements.value;
        document.getElementsByName("PopUpExp_job_id")[0].value = element.attributes.PopUpExp_job_id.value;
        document.getElementsByName("PopUpExp_indice")[0].value = element.attributes.PopUpExp_indice.value;
    };
    //console.log("Fin de _UpdateMisExp");
};

function _UpdateMisEst() {
    // console.log("event.target.name ", event.target.name)
    if (event.target.name === "EST") {
        // console.log("Entro..EST");
        // console.log("Entro..EST");
        // console.log("event.srcElement..", event.srcElement);
        var id = event.srcElement.attributes.PopUpEst_indice.value;
        // console.log("Entro..i", id);
        let element = document.querySelector(`#Est_table tbody tr[PopUpEst_indice$="${id}"]`);
        // console.log("desplegar tipo de estudio")
        // console.log("element.attributes.PopUpEst_edu_type.value; ", element.attributes.PopUpEst_edu_type.value)
        // Activar el PopUp
        document.getElementById("PopUpEst").style.display = "block";
        // document.getElementById("AdicionaJob").focus();

        document.getElementsByName("PopUpEst_edu_title")[0].value = element.attributes.PopUpEst_edu_title.value;
        // document.getElementsByName("PopUpEst_edu_type")[0].value = element.attributes.PopUpEst_edu_type.value;
        document.getElementsByName("PopUpEst_edu_type_sel")[0].value = element.attributes.PopUpEst_edu_type.value;

        // console.log("document.getElementsByName(PopUpEst_edu_type_sel)[0].value ", document.getElementsByName("PopUpEst_edu_type_sel")[0].value)
        document.getElementsByName("PopUpEst_name")[0].value = element.attributes.PopUpEst_name.value;
        document.getElementsByName("PopUpEst_date_start")[0].value = element.attributes.PopUpEst_date_start.value;
        document.getElementsByName("PopUpEst_date_end")[0].value = element.attributes.PopUpEst_date_end.value;
        document.getElementsByName("PopUpEst_edu_id")[0].value = element.attributes.PopUpEst_edu_id.value;
        document.getElementsByName("PopUpEst_indice")[0].value = element.attributes.PopUpEst_indice.value;
    };
    // console.log("Fin de _UpdateMisEst");
};


function _DelMisSkill() {
    //console.log("Entro.._DelMisSkill");
    if (event.target.name === "SKILL") {
        //console.log("Entro..SKILL");
        //console.log("event.srcElement..", event.srcElement);
        var id = event.srcElement.id;
        //console.log("Entro..i", id);
        let element = document.querySelector(`#skills_table tbody tr[id$="${id}"]`);
        element.remove();
    };
};

function _AddMisCateg() {
    // console.log("_AddMisCateg.....")
    if (event.target.name === "CATEGTABLE") {
        let res_partner_category_id = event.srcElement.id;
        // console.log("_AddMisCateg res_partner_category_id=", res_partner_category_id)

        let ele_borrar = document.querySelector(`#categia_table tbody tr[res_partner_category_id$="${res_partner_category_id}"]`);
        let ele_adicionar = ele_borrar.innerHTML
        ele_adicionar = ele_adicionar.replace('CATEGTABLE', 'CATEG')
        ele_adicionar = ele_adicionar.replace('_AddMisCateg(this)', '_DelMisCateg(this)')
        ele_adicionar = ele_adicionar.replace('fa-plus', 'fa-remove')
            // console.log("ele_adicionar ", ele_adicionar)
        let res_partner_category_name = ele_borrar.attributes.name.value
            // console.log("_AddMisCateg res_partner_category_name=", res_partner_category_name)
        ele_borrar.remove();

        let tableRef = document.querySelector(`#categ_table tbody`);
        tableRef.innerHTML = '<tr res_partner_category_id="' + res_partner_category_id + '" name="' + res_partner_category_name + '">' + ele_adicionar + '</tr>' + tableRef.innerHTML
    };
};

function _DelMisCateg() {
    if (event.target.name === "CATEG") {
        //var id = event.srcElement.id;
        let res_partner_category_id = event.srcElement.id;
        // console.log("_DelMisCateg() id=", res_partner_category_id)
        let ele_borrar = document.querySelector(`#categ_table tbody tr[res_partner_category_id$="${res_partner_category_id}"]`);
        let ele_adicionar = ele_borrar.innerHTML
        ele_adicionar = ele_adicionar.replace('CATEG', 'CATEGTABLE')
        ele_adicionar = ele_adicionar.replace('_DelMisCateg(this)', '_AddMisCateg(this)')
        ele_adicionar = ele_adicionar.replace('fa-remove', 'fa-plus')
        let res_partner_category_name = ele_borrar.attributes.name.value
        ele_borrar.remove();

        let tableRef = document.querySelector(`#categia_table tbody`);
        tableRef.innerHTML = '<tr res_partner_category_id="' + res_partner_category_id + '" name="' + res_partner_category_name + '">' + ele_adicionar + '</tr>' + tableRef.innerHTML
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
    const rows = [...table.rows]
    if (rows.length > 0) {
        const props = [...rows[0].attributes].map(a => { return a.name })

        const filas = [...rows].map(r => {
            const entries = [...r.attributes].map((c, i) => {
                return [props[i], c.value];

            });
            return Object.fromEntries(entries);
        });

        return JSON.stringify(filas);
    } else { return [] }
};

function _SkillToJson(input) {
    const table = input
    const rows = [...table.rows].map(r => {
        const entries = [...r.cells].map((c) => {
            return (c.textContent.trim())
        });
        return entries;
    })

    return JSON.stringify(rows);
};