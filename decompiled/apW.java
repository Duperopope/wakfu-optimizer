/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  apX
 *  aqd
 *  aqg
 *  aqk
 *  aql
 *  gnu.trove.map.hash.TIntObjectHashMap
 */
import gnu.trove.map.hash.TIntObjectHashMap;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.EOFException;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FilterInputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.lang.reflect.Field;
import java.nio.Buffer;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;

public class apW
extends apS {
    private static final apX[] cPt = new apX[0];
    private String cPu = null;
    private final TIntObjectHashMap<HashMap<String, ArrayList<aqk>>> cPv = new TIntObjectHashMap();
    private final Object cPw = new Object();
    private final String cPx;
    private final String cPy;
    private boolean cPz;

    public apW(String string, String string2, boolean bl) {
        this.cPx = string;
        this.cPy = string2;
        this.start();
    }

    public apW(String string, String string2) {
        this(string, string2, false);
    }

    @Override
    public apX a(int n, apX apX2) {
        if (!this.blc()) {
            cPe.error("Tentative d'acces au (Simple)BinaryStorage alors qu'il n'est pas initialis\u00e9");
            return null;
        }
        apX[] apXArray = this.a("id", n, apX2);
        if (apXArray != null && apXArray.length > 0) {
            return apXArray[0];
        }
        return null;
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    @Override
    public apX[] a(String string, Object object, apX apX2) {
        if (!this.blc()) {
            cPe.error("Tentative d'acces au (Simple)BinaryStorage alors qu'il n'est pas initialis\u00e9");
            return cPt;
        }
        LinkedList<apX> linkedList = new LinkedList<apX>();
        Object object2 = this.cPw;
        synchronized (object2) {
            HashMap hashMap = (HashMap)this.cPv.get(apX2.aFS());
            if (hashMap == null) {
                return cPt;
            }
            if (hashMap.get(string) == null) {
                return cPt;
            }
            try {
                File file = new File(this.cPu + this.cPx);
                if (!file.exists()) {
                    return cPt;
                }
                String string2 = object.toString();
                for (aqk aqk2 : (ArrayList)hashMap.get(string)) {
                    if (!aqk2.bGv().equals(string2)) continue;
                    try (FileInputStream fileInputStream = new FileInputStream(file);
                         DataInputStream dataInputStream = new DataInputStream(fileInputStream);){
                        FileChannel fileChannel = fileInputStream.getChannel();
                        fileChannel.position(aqk2.bGw());
                        aqg aqg2 = new aqg();
                        aqg2.d(dataInputStream);
                        apX apX3 = apX2.aFN();
                        ByteBuffer byteBuffer = ByteBuffer.wrap(aqg2.aKU());
                        apX3.a(byteBuffer, aqg2.d(), aqg2.bGi());
                        if (byteBuffer.remaining() != 0) {
                            cPe.warn("Objet restaur\u00e9 du simple binary storage : " + byteBuffer.remaining() + " bytes restants non lus [type:" + apX2.aFS() + " | id:" + aqg2.d() + "]");
                        }
                        linkedList.add(apX3);
                        for (aql aql2 : this.cPf) {
                            aql2.c((apS)this, apX3);
                        }
                    }
                }
            }
            catch (FileNotFoundException fileNotFoundException) {
                cPe.error(fileNotFoundException.getMessage(), (Throwable)fileNotFoundException);
            }
            catch (IOException iOException) {
                cPe.error(iOException.getMessage(), (Throwable)iOException);
            }
        }
        if (!linkedList.isEmpty()) {
            return linkedList.toArray(new apX[linkedList.size()]);
        }
        return cPt;
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    @Override
    public apX[] a(apX apX2) {
        if (!this.blc()) {
            cPe.error("Tentative d'acces au (Simple)BinaryStorage alors qu'il n'est pas initialis\u00e9");
            return cPt;
        }
        LinkedList<FileInputStream> linkedList = new LinkedList<FileInputStream>();
        Object object = this.cPw;
        synchronized (object) {
            HashMap hashMap = (HashMap)this.cPv.get(apX2.aFS());
            if (hashMap == null) {
                return cPt;
            }
            try {
                File file = new File(this.cPu + this.cPx);
                if (!file.exists()) {
                    return cPt;
                }
                for (aqk aqk2 : (ArrayList)hashMap.get("id")) {
                    aqg aqg2;
                    Object object2;
                    try (FileInputStream fileInputStream = new FileInputStream(file);){
                        object2 = new DataInputStream(fileInputStream);
                        try {
                            FileChannel fileChannel = fileInputStream.getChannel();
                            fileChannel.position(aqk2.bGw());
                            aqg2 = new aqg();
                            aqg2.d((DataInputStream)object2);
                        }
                        finally {
                            ((FilterInputStream)object2).close();
                        }
                    }
                    fileInputStream = apX2.aFN();
                    object2 = ByteBuffer.wrap(aqg2.aKU());
                    fileInputStream.a((ByteBuffer)object2, aqg2.d(), aqg2.bGi());
                    if (((Buffer)object2).remaining() != 0) {
                        cPe.warn("Objet restaur\u00e9 du simple binary storage : " + ((Buffer)object2).remaining() + " bytes restants non lus [type:" + apX2.aFS() + " | id:" + aqg2.d() + "]");
                    }
                    linkedList.add(fileInputStream);
                    for (aql aql2 : this.cPf) {
                        aql2.c((apS)this, (apX)fileInputStream);
                    }
                }
            }
            catch (FileNotFoundException fileNotFoundException) {
                cPe.error(fileNotFoundException.getMessage(), (Throwable)fileNotFoundException);
            }
            catch (IOException iOException) {
                cPe.error(iOException.getMessage(), (Throwable)iOException);
            }
        }
        if (!linkedList.isEmpty()) {
            return linkedList.toArray(new apX[linkedList.size()]);
        }
        return cPt;
    }

    public void fE(String string) {
        if (string != null) {
            Object object = string;
            if (((String)object).charAt(((String)object).length() - 1) != '/') {
                object = (String)object + "/";
            }
            this.cPz = false;
            this.cPu = object;
        }
    }

    public boolean blc() {
        return this.cPz;
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    @Override
    public boolean bGb() {
        assert (this.cPu != null) : "Il faut initialiser m_baseWorkspace";
        Object object = this.cPw;
        synchronized (object) {
            try {
                File file = new File(this.cPu);
                if (file.exists() && !file.isDirectory()) {
                    throw new RuntimeException("Tentative de changement de workspace [" + this.cPu + "] vers un fichier [not directory] existant [Aborted & Shutdown]");
                }
                if (!file.exists() && !file.mkdirs()) {
                    throw new RuntimeException("Impossible de creer l'arborescence de repertoire [" + this.cPu + "] lors d'un changement de workspace inexistant [Aborted & Shutdown]");
                }
                this.cPv.clear();
                File file2 = new File(this.cPu + this.cPy);
                if (!file2.exists()) {
                    file2.createNewFile();
                    cPe.info("Fichier d'index non trouv\u00e9 pour le chargement de la source binaire : Creation d'une nouvelle source");
                    this.bGg();
                    return true;
                }
                try {
                    FileInputStream fileInputStream = new FileInputStream(file2);
                    try {
                        DataInputStream dataInputStream = new DataInputStream(fileInputStream);
                        try {
                            while (true) {
                                aqk aqk2 = new aqk();
                                aqk2.d(dataInputStream);
                                this.a(aqk2);
                            }
                        }
                        catch (Throwable throwable) {
                            try {
                                dataInputStream.close();
                            }
                            catch (Throwable throwable2) {
                                throwable.addSuppressed(throwable2);
                            }
                            throw throwable;
                        }
                    }
                    catch (Throwable throwable) {
                        try {
                            fileInputStream.close();
                        }
                        catch (Throwable throwable3) {
                            throwable.addSuppressed(throwable3);
                        }
                        throw throwable;
                    }
                }
                catch (EOFException eOFException) {
                }
            }
            catch (IOException iOException) {
                cPe.error(iOException.getMessage(), (Throwable)iOException);
            }
            this.bGg();
            return true;
        }
    }

    private void bGg() {
        this.cPz = true;
        for (aql aql2 : this.cPf) {
            aql2.a((apS)this, this.bGc());
        }
    }

    private void a(aqk aqk2) {
        ArrayList<aqk> arrayList;
        HashMap<String, ArrayList<aqk>> hashMap = (HashMap<String, ArrayList<aqk>>)this.cPv.get(aqk2.aeV());
        if (hashMap == null) {
            hashMap = new HashMap<String, ArrayList<aqk>>(5);
            this.cPv.put(aqk2.aeV(), hashMap);
        }
        if ((arrayList = (ArrayList<aqk>)hashMap.get(aqk2.bGu())) == null) {
            arrayList = new ArrayList<aqk>(300);
            hashMap.put(aqk2.bGu(), arrayList);
        }
        arrayList.add(aqk2);
    }

    @Override
    protected void b(apX apX2) {
        cPe.error("Remove call on a ReadOnlyBinaryStorage");
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    @Override
    protected void c(apX apX2) {
        Object object = this.cPw;
        synchronized (object) {
            byte[] byArray = apX2.aFR();
            if (byArray == null) {
                cPe.error("Tentative de sauvegarde d'un binary storable qui n'a aucun bloc de donn\u00e9es " + String.valueOf(apX2));
                return;
            }
            try {
                long l;
                File file = new File(this.cPu + this.cPx);
                if (!file.exists()) {
                    file.createNewFile();
                }
                try (Field[] fieldArray = new FileOutputStream(this.cPu + this.cPx, true);
                     Field[] fieldArray2 = new DataOutputStream((OutputStream)fieldArray);){
                    FileChannel fileChannel = fieldArray.getChannel();
                    l = fileChannel.size();
                    aqg aqg2 = new aqg(apX2.bGh(), apX2.bGi(), byArray);
                    aqg2.f((DataOutputStream)fieldArray2);
                }
                this.a("id", apX2.bGh(), apX2.aFS(), l);
                for (Field field : fieldArray = apX2.getClass().getDeclaredFields()) {
                    Object object2;
                    if (!field.isAnnotationPresent(aqd.class)) continue;
                    aqd aqd2 = field.getAnnotation(aqd.class);
                    if (field.isAccessible()) {
                        object2 = field.get(apX2);
                    } else {
                        field.setAccessible(true);
                        object2 = field.get(apX2);
                        field.setAccessible(false);
                    }
                    this.a(aqd2.name(), object2, apX2.aFS(), l);
                }
            }
            catch (IOException | IllegalAccessException exception) {
                cPe.error(exception.getMessage(), (Throwable)exception);
            }
        }
    }

    private void a(String string, Object object, int n, long l) {
        try (FileOutputStream fileOutputStream = new FileOutputStream(this.cPu + this.cPy, true);
             DataOutputStream dataOutputStream = new DataOutputStream(fileOutputStream);){
            aqk aqk2 = new aqk(n, string, object.toString(), l);
            aqk2.f(dataOutputStream);
            this.a(aqk2);
        }
        catch (IOException iOException) {
            cPe.error(iOException.getMessage());
        }
    }

    @Override
    protected String bGc() {
        return this.cPu;
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    @Override
    public void bGd() {
        Object object = this.cPw;
        synchronized (object) {
            System.out.println("cleanUpFiles m_baseWorkspace " + this.cPu);
            File file = new File(this.cPu + this.cPy);
            File file2 = new File(this.cPu + this.cPx);
            file.delete();
            file2.delete();
            this.cPv.clear();
        }
    }
}
