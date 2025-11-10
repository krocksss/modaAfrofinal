$(document).ready(function(){
    // Ativa o carrossel de produtos
    $('.product-carousel').owlCarousel({
        loop: false,
        margin: 20,
        nav: true, // Mostra setas de navegação
        dots: true, // Mostra bolinhas de paginação
        responsive:{
            0:{ // Mobile
                items: 2
            },
            768:{ // Tablet/Desktop
                items: 3
            },
            992:{ // Desktop Largo
                items: 4
            }
        }
    });
});
