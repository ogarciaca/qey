window.addEventListener("load", e => {

    console.log("Entro en load");
    document.getElementById("x_photo").attributes.src.value = "data:image/png;base64," + document.getElementsByName("x_photo")[0].value

    let Descargar = document.getElementById("Descargar");

    Descargar.addEventListener("click", e => {
        var opt = {
            margin: 1,
            filename: 'HojadeVida.pdf',
            dpi: 600,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 1 },
            jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
        };
        var element = document.getElementById('main_container');
        html2pdf().set(opt).from(element).save()
    });

})