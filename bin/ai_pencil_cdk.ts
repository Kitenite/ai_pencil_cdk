#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { APP_NAME } from '../lib/constants';
import { PipelineStages } from '../lib/stage';
import { AsynStack } from '../lib/async-stack';

const app = new cdk.App();

const usEast1  = { region: 'us-east-1' };
const usWest2  = { region: 'us-west-2' };

// Test stack
new AsynStack(app, `${APP_NAME}${PipelineStages.BETA}AsyncStack`, {
    stage: PipelineStages.BETA,
    env: usEast1
});

// Prod stack
const asyncStack = new AsynStack(app, `${APP_NAME}${PipelineStages.PROD}AsyncStack`, {
    stage: PipelineStages.PROD,
    env: usWest2
});