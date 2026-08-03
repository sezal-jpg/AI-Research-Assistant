from fastapi import APIRouter
router=APIRouter(tags=['Health'])
@router.get("/")
def root():
    return {
        'project':'OmniResearch AI',
        'status':'Running'
    }
@router.get('Health')
def health():
    return {
        'status':'healthy'
    }    