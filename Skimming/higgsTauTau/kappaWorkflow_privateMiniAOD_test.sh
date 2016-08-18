echo "================= CMSRUN starting ===================="
cmsRun -j FrameworkJobReport.xml -p PSet.py

echo "================= creating softlink for cfipython ===================="
rm -rf $CMSSW_BASE/cfipython
ln $CMSSW_RELEASE_BASE/cfipython $CMSSW_BASE/cfipython -s


cmsDriver.py miniAOD-prod -s PAT --eventcontent MINIAODSIM --runUnscheduled --mc --filein file:root://cms-xrd-global.cern.ch//store/mc/RunIIFall15DR76/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/AODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12_ext1-v1/00000/00120DE2-D9CE-E511-BACE-0025904C51DA.root --fileout file:miniAOD_fromAOD.root --conditions 76X_mcRun2_asymptotic_RunIIFall15DR76_v1  -n 100 --no_exec --python_filename=AODtoMINIAOD_test.py 

cmsRun -p AODtoMINIAOD_test.py
#rm step2.root
echo "================= STEP -AOD to MiniAOD finished ===================="

cp $CMSSW_BASE/src/Kappa/Skimming/higgsTauTau/kSkimming_run2_cfg.py kappa_privateMiniAOD.py
cmsRun -p kappa_privateMiniAOD.py
#rm skimmed_to_reco.root
echo "================= KAPPASKIM finished ===================="

ls -lrth
echo "================= CMSRUN finished ===================="

