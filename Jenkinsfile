def isMainBranch() {
    def branch = env.GIT_BRANCH ?: ''
    return branch == 'origin/main' || branch == 'main' || branch == 'refs/remotes/origin/main'
}

pipeline {
    agent { label 'worker' }

    options {
        timestamps()
        disableConcurrentBuilds()
        gitLabConnection('education-gitlab')
        skipDefaultCheckout true
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Lint') {
            steps {
                updateGitlabCommitStatus name: 'jenkins', state: 'running'
                sh 'docker run --rm -i hadolint/hadolint hadolint - < Dockerfile'
            }
        }

        stage('Build') {
            steps {
                sh 'docker-compose build'
            }
        }

        stage('Test') {
            steps {
                sh 'docker-compose down || true'
                sh 'docker-compose up -d --no-build'
                sh '''
                    attempts=0
                    until curl --silent --fail http://localhost:8000/info > /dev/null; do
                        attempts=$((attempts + 1))
                        if [ "$attempts" -ge 15 ]; then
                            echo "Service did not become ready in time"
                            docker-compose logs || true
                            exit 1
                        fi
                        sleep 1
                    done
                '''
                sh 'curl --fail http://localhost:8000/info'
                sh 'curl --fail "http://localhost:8000/info/currency?currency=USD&date=2023-01-17"'
            }
            post {
                always {
                    sh 'docker-compose logs || true'
                    sh 'docker-compose down || true'
                }
            }
        }

        stage('Manual Approval For Main') {
            when {
                expression { isMainBranch() }
            }
            steps {
                input message: 'Run deploy for main branch?', ok: 'Continue'
            }
        }

        stage('Deploy') {
            when {
                expression { isMainBranch() }
            }
            steps {
                sh 'docker-compose up -d --no-build'
            }
        }
    }

    post {
        success {
            updateGitlabCommitStatus name: 'jenkins', state: 'success'
        }
        failure {
            updateGitlabCommitStatus name: 'jenkins', state: 'failed'
        }
        aborted {
            updateGitlabCommitStatus name: 'jenkins', state: 'canceled'
        }
    }
}
