let mix = require('laravel-mix');

mix.js('front/src/js/app.js', 'homeapp/static/homeapp')
    .sass('front/src/scss/app.scss', 'homeapp/static/homeapp');