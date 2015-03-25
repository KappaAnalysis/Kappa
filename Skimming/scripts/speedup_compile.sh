if [[ -e ${CMSSW_BASE}/config/toolbox/${SCRAM_ARCH}/tools/selected/gcc-cxxcompiler.xml ]]
then
  cp ${CMSSW_BASE}/config/toolbox/${SCRAM_ARCH}/tools/selected/gcc-cxxcompiler.xml ${CMSSW_BASE}/config/toolbox/${SCRAM_ARCH}/tools/selected/gcc-cxxcompiler.xml.backup
  sed -i -e "s@-fipa-pta@@g" ${CMSSW_BASE}/config/toolbox/${SCRAM_ARCH}/tools/selected/gcc-cxxcompiler.xml
fi