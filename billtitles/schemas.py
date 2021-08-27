from typing import List, Optional


from pydantic import BaseModel




class TitleBase(BaseModel):

    title: str

    description: Optional[str] = None




class TitleCreate(TitleBase):

    pass



class Title(TitleBase):
    id: int
    class Config:
        orm_mode = True



class BillBase(BaseModel):

    billnumber: str
    billnumberversion: str




class BillCreate(BillBase):

    billnumber: str
    billnumberversion: str


class Bill(BillBase):
    id: int
    titles: List[Title] = []

    class Config:
        orm_mode = True
