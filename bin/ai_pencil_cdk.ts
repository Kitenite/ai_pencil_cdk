#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { PipelineStack } from '../lib/pipeline-stack';
import { APP_NAME } from '../lib/constants';

const app = new cdk.App();
new PipelineStack(app, `${APP_NAME}PipelineStack`, {});
app.synth();