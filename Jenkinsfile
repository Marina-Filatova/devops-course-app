@Library('my-shared-lib@main') _

// Условия для этапов
def isMR()    { return env.CHANGE_ID != null }
def isMain()  { return env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'master' }
def isTag()   { return env.TAG_NAME != null }

pipeline {
    agent { label 'staging' } // Базовые теги запускаем на стейджинге

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Lint & SAST') {
            parallel {
                stage('Lint') {
                    steps {
                        sh 'echo "Running Lint..." > lint_report.txt' 
                        archiveArtifacts artifacts: 'lint_report.txt'
                    }
                }
                stage('SAST') {
                    steps {
                        sh 'echo "Running SAST..." > sast_report.txt'
                        archiveArtifacts artifacts: 'sast_report.txt'
                    }
                }
            }
        }

        conditionalStage(name: 'Build & Push', condition: isMR() || isMain() || isTag()) {
            sh "docker build -t m_filatova/app:${env.GIT_COMMIT} ."
            // Здесь должна быть логика docker push в твой registry
        }

        conditionalStage(name: 'Deploy to Staging', condition: isMain()) {
            build job: 'app-main-deploy', parameters: [
                string(name: 'IMAGE_TAG', value: env.GIT_COMMIT),
                string(name: 'ENVIRONMENT', value: 'staging')
            ]
        }

        conditionalStage(name: 'Deploy to Production', condition: isTag()) {
            build job: 'app-main-deploy', parameters: [
                string(name: 'IMAGE_TAG', value: env.GIT_COMMIT),
                string(name: 'ENVIRONMENT', value: 'production')
            ]
        }
    }
}