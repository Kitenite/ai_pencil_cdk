import { GoFunction } from "@aws-cdk/aws-lambda-go-alpha";
import { Stack, StackProps } from "aws-cdk-lib";
import { LambdaIntegration, RestApi } from "aws-cdk-lib/aws-apigateway";
import { AttributeType, Table } from "aws-cdk-lib/aws-dynamodb";
import { Function } from "aws-cdk-lib/aws-lambda";
import { Bucket } from "aws-cdk-lib/aws-s3";
import { ISecret, Secret } from "aws-cdk-lib/aws-secretsmanager";
import { Construct } from "constructs";
import { APP_NAME, FIREBASE_SECRET_ARN, STABILITY_SECRET_ARN } from './constants';
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
    // readonly userLambda: Function
    // readonly imageHandlerLambda: Function
    readonly imageToImageLambda: Function
    // readonly feedbackLambda: Function
    // readonly promptStylesLambda: Function

    // Misc
    // readonly firebaseSecret: ISecret
    readonly stabilitySecret: ISecret
    readonly inferenceApi: RestApi

    constructor(scope: Construct, id: string, props: AsycnStackProps) {
        super(scope, id, props);
        this.stage = props.stage
        // Secrets
        // this.firebaseSecret = this.getFirebaseSecret()
        this.stabilitySecret = this.getStabilitySecret()

        // Storage
        // this.userTable = this.createUserTable()
        // this.imageBucket = this.createImageBucket()
        // this.promptTable = this.createPromptTable()
        // this.promptStylesTable = this.createPromptStylesTable()

        // Lambdas
        // this.userLambda = this.createUserLambda()
        // this.feedbackLambda = this.createFeedbackLambda()
        // this.imageHandlerLambda = this.createImageHandlerLambda()
        this.imageToImageLambda = this.createImageToImageLambda()
        // this.promptStylesLambda = this.createPromptStylesLambda()

        // Api
        this.inferenceApi = this.createApi(props.stage)

        // Add permissions. Needs to be after Lambdas.
        // this.userTable.grantReadWriteData(this.userLambda)
        this.stabilitySecret.grantRead(this.imageToImageLambda)
        // this.imageBucket.grantPutAcl(this.imageToImageLambda)
        // this.imageBucket.grantRead(this.imageHandlerLambda)
        // this.imageBucket.grantReadWrite(this.imageHandlerLambda)
        // this.promptStylesTable.grantReadData(this.promptStylesLambda)
    }

    createImageBucket(){
        return new Bucket(this, `${APP_NAME}${this.stage}ImageBucket`, {
            bucketName: `${APP_NAME.toLowerCase()}-${this.stage.toLowerCase()}-image-bucket`,
        })
    }

    createUserTable() {
        const table = new Table(this, `${APP_NAME}${this.stage}UserTable`, {
            tableName: `${APP_NAME}${this.stage}UserTable`,
            partitionKey: { name: 'id', type: AttributeType.STRING },
        });
        return table
    }
    
    createPromptTable() {
        const table = new Table(this, `${APP_NAME}${this.stage}PromptTable`, {
            tableName: `${APP_NAME}${this.stage}PromptTable`,
            partitionKey: { name: 'id', type: AttributeType.STRING },
        });
        return table
    }

    createPromptStylesTable() {
        const table = new Table(this, `${APP_NAME}${this.stage}PromptStylesTable`, {
            tableName: `${APP_NAME}${this.stage}PromptStylesTable`,
            partitionKey: { name: 'id', type: AttributeType.STRING },
        });
        return table
    }

    createImageToImageLambda() {
        return new GoFunction(this, `${APP_NAME}${this.stage}ImageToImageLambda`, {
            entry: './lambda/image-to-image',
            bundling: {
                environment: {
                    // 'IMAGE_BUCKET_NAME': this.imageBucket.bucketName,
                    'STABILITY_SECRET_ARN': this.stabilitySecret.secretArn,
                },
            },
        });
    }

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

    createApi(stage: PipelineStages){
        const inferenceApi = new RestApi(this, `${APP_NAME}${this.stage}InferenceAPI`, {
            description: 'API for async inference',
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
        const imageToImageEndpoint = inferenceApi.root.addResource('image-to-image');
        // const imageEndpoint = inferenceApi.root.addResource('image');
        // const promptStylesEndpoint = inferenceApi.root.addResource('prompt-styles');
        // const feedbackEndpoint = inferenceApi.root.addResource('feedback');

        // userEndpoint.addMethod('POST', new LambdaIntegration(this.userLambda));
        imageToImageEndpoint.addMethod('POST', new LambdaIntegration(this.imageToImageLambda));
        // imageEndpoint.addMethod('POST', new LambdaIntegration(this.imageHandlerLambda));
        // feedbackEndpoint.addMethod('POST', new LambdaIntegration(this.feedbackLambda));
        // promptStylesEndpoint.addMethod('GET', new LambdaIntegration(this.promptStylesLambda));

        return inferenceApi
    }
}