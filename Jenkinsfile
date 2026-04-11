def isMergeRequestBuild() {
    return env.CHANGE_ID?.trim()
}

def isMainlineBranch() {
    return env.BRANCH_NAME in ['main', 'master']
}

def isReleaseTag() {
    return env.TAG_NAME?.trim() && env.TAG_NAME.startsWith('v')
}

pipeline {
    agent none

    options {
        timestamps()
        disableConcurrentBuilds()
        skipDefaultCheckout true
    }

    stages {
        stage('Checkout') {
            agent { label 'staging' }
            steps {
                checkout scm
                sh 'mkdir -p reports'
                echo "BRANCH_NAME=${env.BRANCH_NAME}"
                echo "CHANGE_ID=${env.CHANGE_ID ?: ''}"
                echo "TAG_NAME=${env.TAG_NAME ?: ''}"
            }
        }

        stage('Lint And SAST') {
            parallel {
                stage('Lint') {
                    agent { label 'staging' }
                    steps {
                        checkout scm
                        sh 'mkdir -p reports'
                        sh '''
                            docker run --rm \
                              -v "$PWD:/work" \
                              -w /work \
                              hadolint/hadolint:latest \
                              hadolint Dockerfile -f json > reports/hadolint.json
                        '''
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'reports/hadolint.json', allowEmptyArchive: true, fingerprint: true
                        }
                    }
                }

                stage('SAST') {
                    agent { label 'staging' }
                    steps {
                        checkout scm
                        sh 'mkdir -p reports'
                        sh '''
                            docker run --rm \
                              -v "$PWD:/work" \
                              -w /work \
                              pycqa/bandit:latest \
                              -r . -f json -o reports/bandit.json
                        '''
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'reports/bandit.json', allowEmptyArchive: true, fingerprint: true
                        }
                    }
                }
            }
        }

        stage('Build') {
            when {
                expression {
                    return isMergeRequestBuild() || isMainlineBranch() || isReleaseTag()
                }
            }
            agent { label 'staging' }
            steps {
                checkout scm
                sh 'docker build -t app-main:test .'
            }
        }

        stage('Pipeline Type') {
            agent { label 'staging' }
            steps {
                script {
                    if (isReleaseTag()) {
                        echo 'Release tag pipeline detected.'
                    } else if (isMainlineBranch()) {
                        echo 'Main/master pipeline detected.'
                    } else if (isMergeRequestBuild()) {
                        echo 'Merge request pipeline detected.'
                    } else {
                        echo 'Feature branch pipeline detected.'
                    }
                }
            }
        }
    }
}
