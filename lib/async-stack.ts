import { GoFunction } from "@aws-cdk/aws-lambda-go-alpha";
import { Duration, Stack, StackProps } from "aws-cdk-lib";
import { LambdaIntegration, RestApi } from "aws-cdk-lib/aws-apigateway";
import { AttributeType, Table } from "aws-cdk-lib/aws-dynamodb";
import { Code, Function, LayerVersion, Runtime } from "aws-cdk-lib/aws-lambda";
import { Bucket } from "aws-cdk-lib/aws-s3";
import { ISecret, Secret } from "aws-cdk-lib/aws-secretsmanager";
import { Construct } from "constructs";
import { APP_NAME, FIREBASE_SECRET_ARN, OPEN_AI_SECRET_ARN, STABILITY_SECRET_ARN } from './constants';
import { PipelineStages } from "./stage";

export interface AsycnStackProps extends StackProps {
    stage: PipelineStages
}

export class AsynStack extends Stack {
    readonly stage: PipelineStages

    //Storage
    // readonly userTable: Table
    // readonly imageBucket: Bucket
    // readonly promptTable: Table
    // readonly promptStylesTable: Table

    // Lambda
    readonly lambdaDependencyLayer: LayerVersion
    readonly generateImageLambda: Function
    readonly textToTextLambda: Function
    // readonly userLambda: Function
    // readonly imageHandlerLambda: Function
    // readonly feedbackLambda: Function
    // readonly promptStylesLambda: Function

    // Misc
    // readonly firebaseSecret: ISecret
    readonly stabilitySecret: ISecret
    readonly openAiSecret: ISecret
    readonly api: RestApi

    constructor(scope: Construct, id: string, props: AsycnStackProps) {
        super(scope, id, props);
        this.stage = props.stage
        // Secrets
        // this.firebaseSecret = this.getFirebaseSecret()
        this.stabilitySecret = this.getStabilitySecret()
        this.openAiSecret = this.getOpenAiSecret()

        // Storage
        // this.userTable = this.createUserTable()
        // this.imageBucket = this.createImageBucket()
        // this.promptTable = this.createPromptTable()
        // this.promptStylesTable = this.createPromptStylesTable()

        // Lambdas
        this.lambdaDependencyLayer = this.createLambdaDependencyLayer()
        this.generateImageLambda = this.createGenerateImageLambda()
        this.textToTextLambda = this.createTextToTextLambda()
        // this.userLambda = this.createUserLambda()
        // this.feedbackLambda = this.createFeedbackLambda()
        // this.imageHandlerLambda = this.createImageHandlerLambda()
        // this.promptStylesLambda = this.createPromptStylesLambda()

        // Api
        this.api = this.createApi(props.stage)

        // Add permissions. Needs to be after Lambdas.
        // this.userTable.grantReadWriteData(this.userLambda)
        this.stabilitySecret.grantRead(this.generateImageLambda)
        this.openAiSecret.grantRead(this.textToTextLambda)
        // this.imageBucket.grantPutAcl(this.imageHandlerLambda)
        // this.imageBucket.grantRead(this.imageHandlerLambda)
        // this.imageBucket.grantReadWrite(this.imageHandlerLambda)
        // this.promptStylesTable.grantReadData(this.promptStylesLambda)
    }

    // Get secrets
    getFirebaseSecret() {
        const secret = Secret.fromSecretAttributes(this, "FirebaseKeySecret", {
            secretCompleteArn: FIREBASE_SECRET_ARN
        });
        return secret
    }

    getStabilitySecret() {
        const secret = Secret.fromSecretAttributes(this, "StabilityKeySecret", {
            secretCompleteArn: STABILITY_SECRET_ARN
        });
        return secret
    }

    getOpenAiSecret() {
        const secret = Secret.fromSecretAttributes(this, "OpenAiKeySecret", {
            secretCompleteArn: OPEN_AI_SECRET_ARN
        });
        return secret
    }

    createLambdaDependencyLayer() {
        return new LayerVersion(this, 'dependency-layer', {
            compatibleRuntimes: [
                Runtime.PYTHON_3_7
            ],
            code: Code.fromAsset('./lambda/layer'),
        })
    }

    createImageBucket(){
        return new Bucket(this, `${APP_NAME}${this.stage}ImageBucket`, {
            bucketName: `${APP_NAME.toLowerCase()}-${this.stage.toLowerCase()}-image-bucket`,
        })
    }

    createUserTable() {
        const name = `${APP_NAME}${this.stage}UserTable`
        const table = new Table(this, name, {
            tableName: name,
            partitionKey: { name: 'id', type: AttributeType.STRING },
        });
        return table
    }
    
    createPromptTable() {
        const name = `${APP_NAME}${this.stage}PromptTable`
        const table = new Table(this, name, {
            tableName: name,
            partitionKey: { name: 'id', type: AttributeType.STRING },
        });
        return table
    }

    createPromptStylesTable() {
        const name = `${APP_NAME}${this.stage}PromptStylesTable`
        const table = new Table(this, name, {
            tableName: name,
            partitionKey: { name: 'id', type: AttributeType.STRING },
        });
        return table
    }

    createGenerateImageLambda() {
        const name = `${APP_NAME}${this.stage}GenerateImageLambda`
        return new Function(this, name, {
            functionName: name,
            code: Code.fromAsset('./lambda/'),
            runtime: Runtime.PYTHON_3_7,
            handler: "generate_image.handler",
            timeout: Duration.seconds(900),
            layers: [
                this.lambdaDependencyLayer, 
            ],
            environment: {
                STABILITY_HOST: 'grpc.stability.ai:443',
                STABILITY_KEY_ARN: this.stabilitySecret.secretFullArn?.toString() || STABILITY_SECRET_ARN,
            }
        })
    }

    createTextToTextLambda() {
        const name = `${APP_NAME}${this.stage}TextToTextLambda`
        return new Function(this, name, {
            functionName: name,
            code: Code.fromAsset('./lambda/'),
            runtime: Runtime.PYTHON_3_7,
            handler: "text_to_text.handler",
            timeout: Duration.seconds(900),
            layers: [
                this.lambdaDependencyLayer, 
            ],
            environment: {
                OPEN_AI_KEY_ARN: this.openAiSecret.secretFullArn?.toString() || OPEN_AI_SECRET_ARN,
            }
        })
    }



    createApi(stage: PipelineStages){
        const api = new RestApi(this, `${APP_NAME}${this.stage}API`, {
            description: 'API for Ai Pencil',
            deployOptions: {
                stageName: stage.toString().toLowerCase(),
            },
            defaultCorsPreflightOptions: {
                allowHeaders: [
                    'Content-Type',
                    'X-Amz-Date',
                    'Authorization',
                    'X-Api-Key',
                ],
                allowMethods: ['POST', 'GET'],
                allowCredentials: true,
                allowOrigins: ['http://localhost:3000'],
            },
        });

        // const userEndpoint = inferenceApi.root.addResource('user');
        const generateImageEndpoint = api.root.addResource('generate-image');
        const textToTextEndpoint = api.root.addResource('text-to-text');
        // const imageEndpoint = inferenceApi.root.addResource('image');
        // const promptStylesEndpoint = inferenceApi.root.addResource('prompt-styles');
        // const feedbackEndpoint = inferenceApi.root.addResource('feedback');

        // userEndpoint.addMethod('POST', new LambdaIntegration(this.userLambda));
        generateImageEndpoint.addMethod('POST', new LambdaIntegration(this.generateImageLambda));
        textToTextEndpoint.addMethod('POST', new LambdaIntegration(this.textToTextLambda));
        // imageEndpoint.addMethod('POST', new LambdaIntegration(this.imageHandlerLambda));
        // feedbackEndpoint.addMethod('POST', new LambdaIntegration(this.feedbackLambda));
        // promptStylesEndpoint.addMethod('GET', new LambdaIntegration(this.promptStylesLambda));
        return api
    }
}