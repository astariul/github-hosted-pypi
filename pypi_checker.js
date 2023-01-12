function semverCompare(a, b) {
    if (a.startsWith(b + "-")) return -1
    if (b.startsWith(a + "-")) return  1
    return a.localeCompare(b, undefined, { numeric: true, sensitivity: "case", caseFirst: "upper" })
}

function check_supply_chain_attack(package_name, package_version, callback_if_unsafe) {
    $.ajax({
        type: 'GET',
        crossDomain: true,
        dataType: 'json',
        url: `https://pypi.org/pypi/${package_name}/json`,
        error: function(response) {
            console.log(`Couldn't find ${package_name} on PyPi : you are safe from supply chain attacks.`);
        },
        success: function(jsondata){
            // If the package exists, ensure our package has a higher version
            // And if it doesn't have a higher version, call the callback so that
            // we can take action
            var pypi_vers = jsondata['info']['version'];

            if (semverCompare(package_version, pypi_vers) <= 0) {
                callback_if_unsafe();
            } else {
                console.log(`${package_name} exists on PyPi, but the version is lower (${package_version} > ${pypi_vers}), so you are safe from supply chain attacks.`)
            }
        }
    })
}