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
            stage ('Build'){
                    def imageTag = env.TAG_NAME ?: env.BRANCH_NAME.replace('/', '-')
                    def fullImageName = "mfilatova/currency-rest-api:${imageTag}"
                    
                    echo "Building image: ${fullImageName}"
                    sh "docker build -t ${fullImageName} ."
                    
                    if (isMain() || isTag()) {
                        echo "Pushing to Docker Hub..."
                        withCredentials([usernamePassword(
                            credentialsId: 'docker-hub-credentials',
                            usernameVariable: 'DOCKER_USER',
                            passwordVariable: 'DOCKER_PASS'
                        )]) {
                            sh "docker login -u ${DOCKER_USER} -p ${DOCKER_PASS}"
                            sh "docker push ${fullImageName}"
                        }
                    }                   
                    env.IMAGE_TAG_FOR_DEPLOY = imageTag
            }
        }
        
        if (isMain() || isTag()){
            stage('Deploy'){
                def environment = isMain() ? 'staging' : 'production'
                echo "Deploying ${env.IMAGE_TAG_FOR_DEPLOY} to ${environment}..."
                build job: 'app-main-deploy', parameters: [
                    string(name: 'IMAGE_TAG', value: env.IMAGE_TAG_FOR_DEPLOY),
                    string(name: 'ENVIRONMENT', value: environment)
                ]
            }
        }
    
    if (currentBuild.result == null || currentBuild.result == 'SUCCESS'){
        echo "Pipeline finished with status: SUCCESS"
    }
    else {
        echo "Pipeline finished with status: ${currentBuild.result}"
    }
}