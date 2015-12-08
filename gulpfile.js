var gulp = require('gulp'),
    uglify = require('gulp-uglify'),
    plumber = require('gulp-plumber'),
    browserSync = require('browser-sync');

var reload = browserSync.reload;
var exec = require('child_process').exec;
var app_dir = 'StaticFlask'
var env_setup = false;
browserSync.init
// Uglify javascript
// gulp.task('scripts', function() {
//   gulp.src('js/*.js')
//     .pipe(plumber())
//     .pipe(uglify())
//     .pipe(gulp.dest('build/js'))
// });

function setup_env(){
    exec('source ./venv/bin/activate')
    return true
}

//Run Flask server
gulp.task('runserver', function() {
    if (env_setup == false) {
        env_setup = setup_env()
    }
    var proc = exec('python StaticFlask/__init__.py', function(error, stdout, stderr) {
    console.log('stderr: ' + stderr);
    if (error !== null) {
        console.log('exec error: ' + error);
    }
    });
});

// Default task: Watch Files For Changes & Reload browser
gulp.task('default', ['runserver'], function () {
  browserSync({
    notify: false,
    proxy: "127.0.0.1:5003"
  });
 
  gulp.watch(['StaticFlask/templates/*.*'], reload);
  gulp.watch(['StaticFlask/pages/*,*'], reload);

});
