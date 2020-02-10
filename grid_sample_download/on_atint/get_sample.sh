source ~daits/atScripts/ATLASrucio_setups.sh
MYDSET=$1
MYOWNAREA=$2

# information
id
echo ${XRCPDOOR}
echo ${X509_USER_PROXY}
dir -l ${X509_USER_PROXY}
which gfal-ls

# download the dataset
mkdir -vp ${MYOWNAREA}
cd ${MYOWNAREA}
rucio list-files ${MYDSET}
rucio get ${MYDSET}
