#!/bin/sh
APP_HOME=$(file=$(readlink -f "$0"); dirname "$file")
java -classpath "$APP_HOME/gradle/wrapper/gradle-wrapper.jar" org.gradle.wrapper.GradleWrapperMain "$@"
