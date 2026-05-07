#!/bin/bash

uv build \
    && twine upload dist/* --skip-existing
