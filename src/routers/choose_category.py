@router.post("/{content_id}/platform")
def update_platform(content_id: int, update: FieldUpdate, db: Session = Depends(get_db)):
    return update_field(db, content_id, 'platform_id', update.value)

@router.post("/{content_id}/item")
def update_item(content_id: int, update: FieldUpdate, db: Session = Depends(get_db)):
    return update_field(db, content_id, 'item_id', update.value)

@router.post("/{content_id}/age")
def update_age(content_id: int, update: FieldUpdate, db: Session = Depends(get_db)):
    return update_field(db, content_id, 'age_id', update.value)

@router.post("/{content_id}/gender")
def update_gender(content_id: int, update: FieldUpdate, db: Session = Depends(get_db)):
    return update_field(db, content_id, 'gender_id', update.value)

@router.post("/{content_id}/format")
def update_format(content_id: int, update: FieldUpdate, db: Session = Depends(get_db)):
    return update_field(db, content_id, 'format_id', update.value)

@router.post("/{content_id}/external")
def update_external_data(content_id: int, update: FieldUpdate, db: Session = Depends(get_db)):
    return update_field(db, content_id, 'external_data_id', update.value)

@router.post("/{content_id}/prompt")
def update_user_prompt(content_id: int, update: TextUpdate, db: Session = Depends(get_db)):
    return update_field(db, content_id, 'request_text', update.value)

def update_field(db, content_id, field_name, value):
    content = db.query(Content).filter(Content.content_id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    setattr(content, field_name, value)
    db.commit()
    return {"message": f"{field_name} updated"}