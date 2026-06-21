{
  description = "Development environment for game1";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { nixpkgs, ... }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      devShells = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };
          python = pkgs.python314;
          pythonEnv = python.withPackages (ps: with ps; [
            flask
            flask-migrate
            flask-sqlalchemy
            pillow
            python-dotenv
            requests
            werkzeug
            wikipedia
          ]);
        in
        {
          default = pkgs.mkShell {
            packages = [ pythonEnv pkgs.pyright ];

            shellHook = ''
              export FLASK_APP=app
              export PATH="$PWD/scripts:$PATH"
            '';
          };
        });
    };
}
