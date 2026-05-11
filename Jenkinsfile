@Library('my-shared-lib@main') _

def isMR()    { return env.CHANGE_ID != null }
def isMain()  { return env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'master' }
def isTag()   { return env.TAG_NAME != null }

node('staging') {
        stage('Checkout') {
                checkout scm
        }

        stage('Lint & SAST') {
                    parallel(
                        Lint: {
                            sh '''
                                echo "Date: $(date -u +'%Y-%m-%d %H:%M:%S UTC')" > lint_report.txt
                                docker run --rm -i hadolint/hadolint < Dockerfile >> lint_report.txt 2>&1 || echo "Lint scan completed" >> lint_report.txt
                            '''
                            archiveArtifacts artifacts: 'lint_report.txt'
                        },
                        SAST: {
                            sh '''
                            echo "Date: $(date -u +'%Y-%m-%d %H:%M:%S UTC')" > sast_report.txt
                           bandit -r . -f txt >> sast_report.txt 2>&1 || echo "Bandit scan completed" >> sast_report.txt
                            '''
                            archiveArtifacts artifacts: 'sast_report.txt'
                        }
                    )
        }

        if (isMR() || isMain() || isTag()) {
            stage('Build & Push'){
                def gitSha    = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                def imageTag  = env.TAG_NAME ?: "main-${gitSha}"
                def fullImageName = "mfilatova/currency-rest-api:${imageTag}"

                sh "docker build -t ${fullImageName} ."

                if (isMain() || isTag()) {
                    withCredentials([usernamePassword(
                        credentialsId: 'docker-hub-creditnails',
                        usernameVariable: 'DOCKER_USER'
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        sh '''
                            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        '''
                        sh "docker push ${fullImage}"
                    }
                    echo "Pushed ${fullImage}. ArgoCD Image Updater will handle deploy."
                }

            }
        }
    
    if (currentBuild.result == null || currentBuild.result == 'SUCCESS'){
        echo "Pipeline finished with status: SUCCESS"
    }
    else {
        echo "Pipeline finished with status: ${currentBuild.result}"
    }
}