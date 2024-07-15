{ pkgs, lib, config, inputs, ... }:

{
  # https://devenv.sh/basics/
  env.GREET = "devenv";

  # https://devenv.sh/packages/
  packages = [ pkgs.git pkgs.flyctl pkgs.python311Packages.pip pkgs.poetry];

  # https://devenv.sh/tests/
  enterTest = ''
    echo "Running tests"
    git --version | grep "2.42.0"
  '';

  # https://devenv.sh/services/
  # services.postgres.enable = true;

  # https://devenv.sh/languages/
  languages.python = {
    enable = true;
    venv.enable = true;
    venv.requirements = ''
      langchain
      langchain-openai
      langchain-community
      openai
      chromadb
      tiktoken
      fastapi
      fastapi-sessions
      pysqlite3-binary
    '';
    uv.enable = true;
  };

  # https://devenv.sh/pre-commit-hooks/
  # pre-commit.hooks.shellcheck.enable = true;

  # https://devenv.sh/processes/
  # processes.ping.exec = "ping example.com";

  # See full reference at https://devenv.sh/reference/options/
}
