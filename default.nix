{ pythonPackages, fetchurl, lib }:

let
rethinkdb-driver = pythonPackages.buildPythonPackage rec {
  name = "rethinkdb-2.2.0.post6";
  src = fetchurl {
    url = "https://pypi.python.org/packages/33/e3/ac1b49037765dc96bb4e7464721b567dc674f570ac8983d8ce880dc6e294/rethinkdb-2.2.0.post6.tar.gz";
    sha256 = "1j1bgsncmf6ry9k8bd3a5446cxvqps975x1dv5wzgfaig3wgymib";
  };
};
in pythonPackages.buildPythonPackage {
  name = "logcentral-logshipper";
  src = lib.sourceFilesBySuffices ./. [".py"];
  propagatedBuildInputs = [ rethinkdb-driver pythonPackages.ipython ];
}
